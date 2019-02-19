import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import time
import chardev
from abc import ABCMeta, abstractmethod
import struct

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
        wb = chardev.whileBreaker(5)
        while(True):
            time.sleep(0.3)
            self.forwardwrite(CIapDev.byteGoCmd)
            if(self.confirmack() is False):
                wb()
                continue
            cmd = CIapDev.getbytesfromuint32(address)
            cmd.append(self.getxor(cmd))
            self.forwardwrite(cmd)
            if(self.confirmack() is False):
                wb()
                continue
            else:
                print('finished')
                break
            
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

    def restorebootparam(self, blockaddr):
        print('restoring boot param...')
        powerupvarnum = self.readuint32(blockaddr + 4)

        DEFAULT_SUIT_VAL_NUM = 2
        suitvarnum = DEFAULT_SUIT_VAL_NUM
        if powerupvarnum > 0xffff:
            suitvarnum = DEFAULT_SUIT_VAL_NUM
        else:
            suitvarnum = powerupvarnum

        print('var num: %d' % suitvarnum)

        xorresult = 0
        for i in range(0, suitvarnum):
            xorresult = xorresult ^ self.readuint32(blockaddr + 4 * i)

        if xorresult != self.readuint32(blockaddr + 4 * suitvarnum):
            print('power up field XOR mismatch')
            suitvarnum = DEFAULT_SUIT_VAL_NUM

        powerupval = []
        if suitvarnum != DEFAULT_SUIT_VAL_NUM:
            for i in range(0, suitvarnum):
                powerupval += [self.readuint32(blockaddr + 4 * i)]
        else:
            powerupval = [0, 2]

        powerupval[0] = 0x5555aaaa
        xorresult = 0
        for i in range(0, suitvarnum):
            xorresult = xorresult ^ powerupval[i]
            self.loaduint32(powerupval[i], blockaddr + 4 * i)

        self.loaduint32(xorresult, blockaddr + 4 * suitvarnum)
        print('restore boot parameters finished')

    def setInLoadingBin(self, blockaddr):
        powerupval = 0x66668888
        self.loaduint32(powerupval, blockaddr)

    def setInBL(self, blockaddr):
        powerupval = 0x2b2b6666
        self.loaduint32(powerupval, blockaddr)

    def getbootloaderversion(self):
        self._chardev.ioctl('useSeconAddress')
        print('read firmware version with second address')
        wb = chardev.whileBreaker(6)
        timeOutCnt = 0
        while True:
            self.forwardwrite(CIapDev.byteGetFirmwareVersion)
            stmback = self._chardev.read(5)
            if(stmback == b''):
                # print('read timeout, maybe port unmatch, switch to primeAddress')
                # self._chardev.ioctl('usePrimeAddress')
                print('read timeout')
                if(timeOutCnt < 8):
                    timeOutCnt = timeOutCnt + 1
                    continue
                else:
                    return 0x01
                continue
            elif(stmback[0] != CIapDev.ACK[0]):
                print('not ack', stmback)
                wb()
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
        wb = chardev.whileBreaker(7, 20)
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
                wb()
                continue
            # send address
            byteAddress = CIapDev.getbytesfromuint32(nowDownloadAddress)
            byteAddress.append(CIapDev.getxor(byteAddress))
            self.forwardwrite(byteAddress)
            if self.confirmack() is False:
                wb()
                continue
            # send data
            self.forwardwrite(slipArray)
            if self.confirmack() is False:
                wb()
                continue
            i = j

    def loaduint32(self, val, address):
        data = bytearray(struct.pack('<I', val))
        data.insert(0, 3)
        data.append(CIapDev.getxor(data))
        wb = chardev.whileBreaker(8)
        while True:
            # send head
            self.forwardwrite(CIapDev.byteWriteMemCmd)
            if self.confirmack() is False:
                wb()
                continue
            # send address
            byteAddress = CIapDev.getbytesfromuint32(address)
            byteAddress.append(CIapDev.getxor(byteAddress))
            self.forwardwrite(byteAddress)
            if self.confirmack() is False:
                wb()
                continue
            # send data
            self.forwardwrite(data)
            if self.confirmack() is False:
                time.sleep(1)
                wb()
                continue
            else:
                print('write 0x%04X to addr 0x%04X success' % (val, address))
                break

    def readuint32(self, address):
        wb = chardev.whileBreaker(9)
        while True:
            # send head
            self.forwardwrite(CIapDev.byteReadMemCmd)
            if self.confirmack() is False:
                wb()
                continue

            # send address
            byteAddress = CIapDev.getbytesfromuint32(address)
            byteAddress.append(CIapDev.getxor(byteAddress))
            self.forwardwrite(byteAddress)
            if self.confirmack() is False:
                wb()
                continue

            # send datalength
            double_datalen = bytearray([4 - 1, 4 - 1])
            self.forwardwrite(double_datalen)
            if self.confirmack() is False:
                wb()
                continue

            # read data
            stmback = self._chardev.read(4)
            checkbyte = self._chardev.read(1)
            if self.getxor(bytearray(stmback)) == checkbyte[0]:
                (val,) = struct.unpack('<I', stmback)
                print('read uint32 0x%08X' % val)
                return val
            else:
                print("check sum failed, calc: 0x%X, get: 0x%X, data: %s" %
                      (self.getxor(bytearray(stmback)), checkbyte[0], stmback))
                wb()
                continue

    def readbin(self, filename, address=0x08000000):
        # get flasher file, read only, binary
        if(0 == address):
            address = self._addrApp
        READ_DATA_LEN = 256
        f = open(filename, 'wb')
        i = 0
        length = 800000
        wb = chardev.whileBreaker(10,10)
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
                wb()
                continue

            # send address
            byteAddress = CIapDev.getbytesfromuint32(nowReadAddress)
            byteAddress.append(CIapDev.getxor(byteAddress))
            self.forwardwrite(byteAddress)
            if self.confirmack() is False:
                wb()
                continue

            # send datalength
            double_datalen = bytearray([slipLen - 1, slipLen - 1])
            self.forwardwrite(double_datalen)
            if self.confirmack() is False:
                wb()
                continue

            # read data
            try:
                stmback = self._chardev.read(256)
            except KeyboardInterrupt:
                f.close()
                quit()

            checkbyte = self._chardev.read(1)
            if self.getxor(bytearray(stmback)) == checkbyte[0]:
                if self.isallbytes0xff(stmback):
                    print("all byte 0xFF, read finished")
                    f.close()
                    break
                else:
                    f.write(stmback)
            else:
                print("check sum failed, calc: 0x%X, get: 0x%X, data: %s" %
                      (self.getxor(bytearray(stmback)), checkbyte[0], stmback))
                wb()
                continue

            i = j


def test_isallbytes0xff():
    assert CIapDev.isallbytes0xff(b'\xff'*50) is True
    assert CIapDev.isallbytes0xff(b'\xfd') is False
