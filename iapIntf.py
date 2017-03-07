import sys
import time
import charDev

print('start')

class CIapDev(object):

    ACK = b'\x79'
    NACK = b'\x1F'

    byteReset = bytearray(b'\x09\x00\x00\x00\xff\xff\xff\xff')
    byteJump2BL = bytearray(b'\x07\x00\x00\x00\xff\xff\xff\xff')
    byteBoot2BL = bytearray(b'\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f')

    byteWriteMemCmd = bytearray(b'\x31\xCE')
    byteReadMemCmd = bytearray(b'\x11\xEE')
    byteGoCmd = bytearray(b'\x21\xDE')
    byteGetFirmwareVersion = bytearray(b'\x01\xFE')

    byteBootParam_BL = bytearray(b'\x66\x66\x2b\x2b')
    byteBootParam_APP = bytearray(b'\xaa\xaa\x55\x55')

    def __init__(self, charDevice, flashMap):
        self._charDev = charDevice
        self._addrBootLoader = CIapDev.getBytesFromUint32(flashMap[0])
        self._addrBootParam = CIapDev.getBytesFromUint32(flashMap[1])
        self._addrApp = CIapDev.getBytesFromUint32(flashMap[2])

    @staticmethod
    def getXor(val):
        xor = 0
        for byte in val:
            xor ^= byte
        return xor
    
    @staticmethod
    def getBytesFromUint32(val):
        val0 = val & 0xFF
        val1 = (val & 0xFF00) >> 8
        val2 = (val & 0xFF0000) >> 16
        val3 = (val & 0xFF000000) >> 24
        return bytearray([val3,val2,val1,val0])

    @staticmethod
    def isAllBytesFF(val):
        for byte in val:
            if byte != 255:
                return False
        return True

    def run(self):
        self._charDev.run()

    def confirm_ack(self):
        stmback = self._charDev.read(1)
        if stmback != CIapDev.ACK:
            print('not ack:'+ str(stmback))
            return False
        else:
            return True

    def jumpToApp(self):
        print('jumping to application')
        while(True):
            self._charDev.clearReadBuf()
            self._charDev.write(CIapDev.byteGoCmd)
            stmback = self._charDev.read(1)
            if(stmback != CIapDev.ACK):
                print("1get",stmback,", resend")
                continue
            cmd = self._addrApp
            cmd.append(self.getXor(self._addrApp))
            self._charDev.write(cmd)
            stmback = self._charDev.read(1)
            if(stmback != CIapDev.ACK):
                print("2get",stmback,", resend")
                continue
            else:
                break
            sys.stdout.flush()

    def jumpToBootloader(self):
        print('jump to bootloader')
        sys.stdout.flush()
        while True:
            self._charDev.clearReadBuf()
            self._charDev.write(CIapDev.byteJump2BL)
            stmback = self._charDev.read(1)
            if(stmback == b''):
                print('timeout')
                continue
            elif(stmback == CIapDev.NACK):
                print('already in bootloader')
                break
            elif(stmback == b'\x07'):
                print('from application')
                break
            else:
                print('get byte', stmback)
                continue
            print('resend jump command')
            sys.stdout.flush()
    
    def resetToBootloader(self):
        print('reset to bootloader')
        isInApp = True
        self._charDev.write(CIapDev.byteReset)
        stmback = self._charDev.read(1)
        if(stmback == CIapDev.NACK[0]):
            time.sleep(0.5)
            self._charDev.clearReadBuf()
            print('already in bootloader')
            isInApp = False
        while(isInApp):
            self._charDev.write(CIapDev.byteBoot2BL)
            if(stmback == CIapDev.NACK[0]):
                time.sleep(0.1)
                self._charDev.clearReadBuf()
                break
            else:
                self._charDev.clearReadBuf()

    def writeBootParam(self, val:'bootpram enum'):
        if(val != CIapDev.byteBootParam_BL 
        and val != CIapDev.byteBootParam_APP):
            print('boot param error:', val)
            return
        print('write bootparam')
        self._charDev.write(CIapDev.byteWriteMemCmd)
        cmd = self._addrBootParam
        cmd.append(CIapDev.getXor(self._addrBootParam))
        self._charDev.write(cmd)
        cmd = bytearray(b'\x03') + val
        cmd.append(CIapDev.getXor(cmd))
        self._charDev.write(cmd)
        self._charDev.clearReadBuf()
        

    def getBootLoaderVersion(self):
        return 0x00

    def loadBin(self, filename, address):
        SEND_DATA_LEN = 256
        tail = filename[-4:]
        if tail != ".bin":
            print("the extension is not .bin")
            return False
        f = open(filename,'rb')
        data = f.read()
        i = 0
        length = len(data)
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
            slipArray.insert(0,slipLen - 1)
            slipArray.append(CIapDev.getXor(slipArray))
            # send head
            self._charDev.write(CIapDev.byteWriteMemCmd)
            if self.confirm_ack() != True:
                continue
            #send address
            byteAddress = CIapDev.getBytesFromUint32(nowDownloadAddress)
            byteAddress.append(CIapDev.getXor(byteAddress))
            self._charDev.write(byteAddress)
            if self.confirm_ack() != True:
                continue
            #send data
            self._charDev.write(slipArray)
            if self.confirm_ack() != True:
                continue
            i = j

    def readBin(self, filename, address):
        # get flasher file, read only, binary
        READ_DATA_LEN = 256
        f = open(filename,'wb')
        i = 0
        loopCondition = True
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
            self._charDev.write(CIapDev.byteReadMemCmd)
            if self.confirm_ack() != True:
                continue

            #send address
            byteAddress = CIapDev.getBytesFromUint32(nowReadAddress)
            byteAddress.append(CIapDev.getXor(byteAddress))
            self._charDev.write(byteAddress)
            if self.confirm_ack() != True:
                continue

            #send datalength
            double_datalen = bytearray([slipLen-1, slipLen-1])
            self._charDev.write(double_datalen)
            if self.confirm_ack() != True:
                continue

            #read data
            stmback = self._charDev.read(1)
            checkbyte = self._charDev.read(1)
            if self.getXor(bytearray(stmback)) == ord(checkbyte):
                if self.isAllBytesFF(stmback):
                    print("all byte 0xFF, read finished")
                    f.close()
                    break
                else:
                    f.write(stmback)
            else:
                print("check sum failed")
                print("calc = 0x%X" %self.getXor(bytearray(stmback)))
                print("get = 0x%X" % ord(checkbyte))
                continue

            i = j

