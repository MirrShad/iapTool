from iapdev import *
from chardev import *
import struct
import socket


class CF4KernelIapDev(CIapDev):

    def __init__(self, charDevice):
        CIapDev.__init__(self, charDevice)

    def resetBoard(self):
        pass

    def settargetboardbootloader(self):
        print('Set F4Kernel to bootloader')
        GET_APP_VERSION_CMD = 0
        while True:
            self._chardev.ioctl("usePrimeAddress")

        while True:
            cmd_bytes = struct.pack(
                '<2I', GET_APP_VERSION_CMD, 0xffffffff)
            self._chardev.ioctl("clearReadBuf")
            self._chardev.write(cmd_bytes)
            databuff = bytearray(b'')
            while True:
                databack = self._chardev.read(1)
                if b'' == databack:
                    break
                else:
                    databuff += bytearray(databack)

            if(0 == len(databuff)):
                print('No reply, may be old version')
            if databack is b'':
                print('reset SeerDIO forward mode timeout')
                continue
            elif databack == bytearray(cmd_bytes):
                print('reset SeerDIO forward mode ok')
                break
            else:
                print('reset forward mode faild, get:')
                print(databack)
                time.sleep(0.5)
                continue

    def resetToBootloader(self):
        print('reset to bootloader not supported')

    def setforwardmode(self):
        pass

    def resetforwardmode(self):
        pass

    def resettargetboard(self):
        pass

    def forwardwrite(self, data):
        self._chardev.ioctl("clearReadBuf")
        self._chardev.write(data)
