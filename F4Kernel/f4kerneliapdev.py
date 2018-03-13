import sys
sys.path.append('../')

from iapdev.iapdev import CIapDev
from chardev.chardev import CCharDev, whileBreaker
import struct
import socket
import time


class CF4KernelIapDev(CIapDev):

    def __init__(self, charDevice):
        CIapDev.__init__(self, charDevice)

    def resetBoard(self):
        pass

    def settargetboardbootloader(self):

        if self.checktargetboardinbootloader():
            return

        print('Set F4Kernel to bootloader')
        GET_APP_VERSION_CMD = 0x1032
        SET_TO_BOOTLOADER_CMD = 0x101D

        QUERY_APP_VERSION_MSG = struct.pack(
            '<2I', GET_APP_VERSION_CMD, 0xffffffff)
        JUMP_TO_BL_MSG = struct.pack('<2I', SET_TO_BOOTLOADER_CMD, 0xFFFFFFFF)

        # confirm current firmware version
        wb = whileBreaker(2)
        wbb = whileBreaker(3)
        while True:
            self._chardev.ioctl("usePrimeAddress")
            self._chardev.write(QUERY_APP_VERSION_MSG)
            backParamNum = 4
            versionrawmsg = self._chardev.read(backParamNum * 4)

            if(len(versionrawmsg) != backParamNum * 4):
                print('invalid back message: %s' % versionrawmsg)
                wb()
                continue

            (head, v0, v1, v2) = struct.unpack('<4I', versionrawmsg)

            if(head != GET_APP_VERSION_CMD):
                print('pack head error: 0x%X' % head)
                wbb()
                continue

            print('Get app version: %d.%d.%d' % (v0, v1, v2))
            if(v0 < 1 or v1 < 7 or v2 < 904):
                print('App version do not support auto update, press enter to exit...')
                time.sleep(1)
                sys.exit(4)

            print('Version confirm ok!')
            break

        wb = whileBreaker(2)
        wbb = whileBreaker(3)
        while True:
            self._chardev.write(JUMP_TO_BL_MSG)
            backParamNum = 2
            stmback = self._chardev.read(backParamNum * 4)
            if(len(stmback) != backParamNum * 4):
                print('invalid back message: %s' % stmback)
                wb()
                continue
            (head, val) = struct.unpack('<2I', stmback)

            if(head != SET_TO_BOOTLOADER_CMD):
                print('pack head error: 0x%X' % head)
                wbb()
                continue

            break

        self._chardev.ioctl("useSeconAddress")
        time.sleep(0.5)

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

    def checktargetboardinbootloader(self):
        self._chardev.ioctl("useSeconAddress")
        self._chardev.write(b'\xff' * 10)
        try:
            stmback = self._chardev.read(4)
        except WindowsError:
            return

        if stmback == b'\x1f' * 4:
            print('Already in bootloader!')
            return True
        else:
            return False
