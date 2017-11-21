import sys
import os
import time
import chardev
from abc import ABCMeta, abstractmethod

print('start')


class CIapDev(object):

    ACK = b'\x79'
    NACK = b'\x1F'

    byteWriteMemCmd = bytearray(b'\x31\xCE')
    byteReadMemCmd = bytearray(b'\x11\xEE')
    byteGoCmd = bytearray(b'\x21\xDE')
    byteGetFirmwareVersion = bytearray(b'\x01\xFE')

    byteBootParam_BL = bytearray(b'\x66\x66\x2b\x2b')
    byteBootParam_APP = bytearray(b'\xaa\xaa\x55\x55')

    def __init__(self, charDevice):
        self._chardev = charDevice
        self._chardev.open()

    @staticmethod
    def getxor(val):
        xor = 0
        for byte in val:
            xor ^= byte
        return xor

    @staticmethod
    def getbytesfromuint32(val):
        val0 = val & 0xFF
        val1 = (val & 0xFF00) >> 8
        val2 = (val & 0xFF0000) >> 16
        val3 = (val & 0xFF000000) >> 24
        return bytearray([val3, val2, val1, val0])

    @staticmethod
    def isallbytes0xff(val):
        for byte in val:
            if byte != 255:
                return False
        return True

    def confirmack(self):
        stmback = self._chardev.read(1)
        if stmback.__len__() == 0 or stmback[0] != CIapDev.ACK[0]:
            print('not ack:' + str(stmback))
            self._chardev.clearReadBuf()
            return False
        else:
            return True

    def jumpToAddress(self, address=0):
        if(0 == address):
            address = self._addrApp
        print('jump to address: 0x%X' % address)
        while(True):
            self.forwardwrite(CIapDev.byteGoCmd)
            if(self.confirmack() is False):
                continue
            cmd = CIapDev.getbytesfromuint32(address)
            cmd.append(self.getxor(cmd))
            self.forwardwrite(cmd)
            if(self.confirmack() is False):
                continue
            else:
                break
            print('finished')
            sys.stdout.flush()

    @abstractmethod
    def resetBoard(self):
        pass

    @abstractmethod
    def resetToBootloader(self):
        pass

    @abstractmethod
    def setforwardmode(self):
        pass

    @abstractmethod
    def resetforwardmode(self):
        pass

    @abstractmethod
    def settargetboardbootloader(self):
        pass

    @abstractmethod
    def resettargetboard(self):
        pass

    @abstractmethod
    def forwardwrite(self, val):
        pass

    def getbootloaderversion(self):
        self._chardev.ioctl('useSeconAddress')
        print('read firmware version with second address')
        while True:
            self.forwardwrite(CIapDev.byteGetFirmwareVersion)
            stmback = self._chardev.read(5)
            if(stmback == b''):
                print('read timeout, maybe port unmatch, switch to primeAddress')
                self._chardev.ioctl('usePrimeAddress')
                continue
            elif(stmback[0] != CIapDev.ACK[0]):
                print('not ack', stmback)
                continue
            else:
                return stmback[1]

        return 0x00

    def loadbin(self, filename, address):
        if(0 == address):
            address = self._addrApp
        SEND_DATA_LEN = 256
        tail = filename[-4:]
        if tail != ".bin":
            print("the extension is not .bin")
            return False
        f = open(filename, 'rb')
        data = f.read()
        i = 0
        length = len(data)
        print('bin file length = %d' % length)
        while i < length:
            nowDownloadAddress = address + i
            print("write address 0x%X" % nowDownloadAddress)
            sys.stdout.flush()
            j = i + SEND_DATA_LEN
            if j > length:
                j = length
            slip = data[i:j]
            slipLen = j - i
            slipArray = bytearray(slip)
            slipArray.insert(0, slipLen - 1)
            slipArray.append(CIapDev.getxor(slipArray))
            # send head
            self.forwardwrite(CIapDev.byteWriteMemCmd)
            if self.confirmack() is False:
                continue
            # send address
            byteAddress = CIapDev.getbytesfromuint32(nowDownloadAddress)
            byteAddress.append(CIapDev.getxor(byteAddress))
            self.forwardwrite(byteAddress)
            if self.confirmack() is False:
                continue
            # send data
            self.forwardwrite(slipArray)
            if self.confirmack() is False:
                continue
            i = j

    def loaduint32(self, val, address):
        data = CIapDev.getbytesfromuint32(val)
        data.insert(0, 3)
        data.append(CIapDev.getxor(data))
        print(data)
        while True:
            # send head
            self.forwardwrite(CIapDev.byteWriteMemCmd)
            if self.confirmack() is False:
                continue
            # send address
            byteAddress = CIapDev.getbytesfromuint32(address)
            byteAddress.append(CIapDev.getxor(byteAddress))
            self.forwardwrite(byteAddress)
            if self.confirmack() is False:
                continue
            # send data
            self.forwardwrite(data)
            if self.confirmack() is False:
                time.sleep(1)
                continue
            else:
                print('write 0x%04X to addr 0x%04X success' % (val, address))
                break

    def readbin(self, filename, address):
        # get flasher file, read only, binary
        if(0 == address):
            address = self._addrApp
        READ_DATA_LEN = 256
        f = open(filename, 'wb')
        i = 0
        length = 80000
        while i < length:
            nowReadAddress = address + i
            print("read address 0x%X" % nowReadAddress)
            sys.stdout.flush()
            j = i + READ_DATA_LEN
            if j > length:
                j = length
            slipLen = j - i

            # send head
            self.forwardwrite(CIapDev.byteReadMemCmd)
            if self.confirmack() is False:
                continue

            # send address
            byteAddress = CIapDev.getbytesfromuint32(nowReadAddress)
            byteAddress.append(CIapDev.getxor(byteAddress))
            self.forwardwrite(byteAddress)
            if self.confirmack() is False:
                continue

            # send datalength
            double_datalen = bytearray([slipLen - 1, slipLen - 1])
            self.forwardwrite(double_datalen)
            if self.confirmack() is False:
                continue

            # read data
            stmback = self._chardev.read(256)
            checkbyte = self._chardev.read(1)
            if self.getxor(bytearray(stmback)) == checkbyte[0]:
                if self.isallbytes0xff(stmback):
                    print("all byte 0xFF, read finished")
                    f.close()
                    break
                else:
                    f.write(stmback)
            else:
                print("check sum failed")
                print(stmback)
                print("calc = 0x%X" % self.getxor(bytearray(stmback)))
                print("get = 0x%X" % checkbyte[0])
                continue

            i = j
