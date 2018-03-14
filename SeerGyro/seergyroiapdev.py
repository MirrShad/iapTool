import sys
sys.path.append('../')

from chardev.chardev import *
from iapdev.iapdev import *
import struct
import socket
import time


class CSeerGyroIapDev(CIapDev):
    GYROCMD_PACKHEAD = 0x0000A001
    GYROIAP_PACKHEAD = 0x00009999
    GYROIAP_NORMAL_REPLY = struct.pack('<I',0)

    def __init__(self, charDevice):
        CIapDev.__init__(self, charDevice)

    def resetBoard(self):
        pass

    def settargetboardbootloader(self):
        print('Gyro is already in bootloader when set SeerDIO board to forward mode')

    def resetToBootloader(self):
        print('reset to bootloader not supported')

    def setforwardmode(self):
        print('set SeerDIO forward mode')

        ADD_TASK_CMD_HEAD = 0xA002
        GYRO_TASK_ID = 102

        wb = whileBreaker(11,10)
        while True:
            cmd_bytes = struct.pack(
                '<2I', ADD_TASK_CMD_HEAD, GYRO_TASK_ID)
            self._chardev.write(cmd_bytes)
            databack = self._chardev.read(4)
            if databack is b'':
                print('Launch gyro task timeout')
                wb()
                continue
            elif databack == self.GYROIAP_NORMAL_REPLY:
                break
            else:
                print('Launch gyro task, get:')
                print(databack)
                break

        print('Gyro must be set to bootloader before set forward mode')
        SET_GYRO_JUMP_BOOTLOADER = 0x05
        wb = whileBreaker(12)
        while True:
            cmd_bytes = struct.pack(
                '<2I', self.GYROCMD_PACKHEAD, SET_GYRO_JUMP_BOOTLOADER)
            self._chardev.write(cmd_bytes)
            databack = self._chardev.read(4)
            if databack is b'':
                print('set gyro to bootloader failed')
                wb()
                continue
            elif databack == self.GYROIAP_NORMAL_REPLY:
                break
            else:
                print('set gyro to bootloader, get:')
                print(databack)
                break

        SET_IAP_FLAG_CMD = 0x01
        wb = whileBreaker(13)
        while True:
            cmd_bytes = struct.pack(
                '<2I', self.GYROCMD_PACKHEAD, SET_IAP_FLAG_CMD)
            self._chardev.write(cmd_bytes)
            databack = self._chardev.read(4)
            if databack is b'':
                print('set SeerDIO forward mode timeout')
                wb()
                continue
            elif databack == self.GYROIAP_NORMAL_REPLY:
                break
            else:
                print('set forward mode ok, get:')
                print(databack)
                break

    def resetforwardmode(self):
        print('reset SeerDIO IMU forward mode')
        RESET_IAP_FLAG_CMD = 0x02
        wb = whileBreaker(14)
        while True:
            cmd_bytes = struct.pack(
                '<2I', self.GYROCMD_PACKHEAD, RESET_IAP_FLAG_CMD)
            self._chardev.ioctl("clearReadBuf")
            self._chardev.write(cmd_bytes)
            databack = self._chardev.read(4)
            if databack is b'':
                print('reset SeerDIO forward mode timeout')
                wb()
                continue
            elif databack == self.GYROIAP_NORMAL_REPLY:
                break
            else:
                print('reset forward mode ok, get:')
                print(databack)
                break

    def resettargetboard(self):
        print('reset to  not supported')

    def forwardwrite(self, data):
        pack = struct.pack('<I' + str(len(data)) + 's',
                           self.GYROIAP_PACKHEAD, data)
        self._chardev.ioctl("clearReadBuf")
        self._chardev.write(pack)
