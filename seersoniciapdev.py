from iapdev import *
from chardev import *
import struct
import socket


class CSeerSonicIapDev(CIapDev):
    SONICCMD_PACKHEAD = 0x00001046
    SONICIAP_PACKHEAD = 0x00001045
    SONICMODBUS_SLAVE_ADDR = 1
    SONICMODBUS_IAP_FLAG_OFFS = 1
    SONICMODBUS_RESET_BRD_OFFS = 0
    # set sonicmodbus IAP flag
    MODBUS_WRITE_REG_CODE = 0x06
    WRITE_DATA_NUM = 1
    SET_IAP_CRC_RESULT = 0xCA19
    RESET_BRD_CRC_RESULT = 0x0A48

    def __init__(self, charDevice):
        CIapDev.__init__(self, charDevice)

    def resetBoard(self):
        pass

    def settargetboardbootloader(self):
        # 01 06 00 01 00 01
        while True:
            set_iap_bytes = struct.pack('>2B2H',
                                        self.SONICMODBUS_SLAVE_ADDR,
                                        self.MODBUS_WRITE_REG_CODE,
                                        self.SONICMODBUS_IAP_FLAG_OFFS,
                                        self.WRITE_DATA_NUM)
            set_iap_bytes = struct.pack('<' + str(len(set_iap_bytes)) + 'sH',
                                        set_iap_bytes, self.SET_IAP_CRC_RESULT)
            self.forwardwrite(set_iap_bytes)
            dataque = bytearray(b'')
            while len(dataque) < 8:
                byteback = self._chardev.read(1)
                if byteback is b'':
                    break
                else:
                    dataque += byteback
            if len(dataque) == 0:
                print('set target board IAP flag timeout')
                continue
            elif dataque[0] is 0x1f:
                print('already in bootloader')
                return
            elif dataque == bytearray(set_iap_bytes):
                print('set target board to bootloader ok')
                break
            else:
                print(dataque)

    def resetToBootloader(self):
        print('reset to bootloader not supported')

    def setforwardmode(self):
        print('set SeerDIO forward mode')

        LAUNCH_SONIC_TASK_CMD = 6
        while True:
            cmd_bytes = struct.pack(
                '<2I', self.SONICCMD_PACKHEAD, LAUNCH_SONIC_TASK_CMD)
            self._chardev.write(cmd_bytes)
            databack = self._chardev.read(8)
            if databack is b'':
                print('Lanch sonic modbus task timeout')
                continue
            elif databack == bytearray(cmd_bytes):
                break
            else:
                print('Lanch sonic modbus task, get:')
                print(databack)
                continue

        SET_IAP_FLAG_CMD = 3
        while True:
            cmd_bytes = struct.pack(
                '<2I', self.SONICCMD_PACKHEAD, SET_IAP_FLAG_CMD)
            self._chardev.write(cmd_bytes)
            databack = self._chardev.read(8)
            if databack is b'':
                print('set SeerDIO forward mode timeout')
                continue
            elif databack == bytearray(cmd_bytes):
                break
            else:
                print('set forward mode faild, get:')
                print(databack)
                continue

    def resetforwardmode(self):
        print('reset SeerDIO forward mode')
        RESET_IAP_FLAG_CMD = 4
        while True:
            cmd_bytes = struct.pack(
                '<2I', self.SONICCMD_PACKHEAD, RESET_IAP_FLAG_CMD)
            self._chardev.ioctl("clearReadBuf")
            self._chardev.write(cmd_bytes)
            databack = self._chardev.read(8)
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

    def resettargetboard(self):
        # 01 06 00 01 00 01
        while True:
            print('try reset target board')
            reset_target_bytes = struct.pack('>2B2H',
                                             self.SONICMODBUS_SLAVE_ADDR,
                                             self.MODBUS_WRITE_REG_CODE,
                                             self.SONICMODBUS_RESET_BRD_OFFS,
                                             self.WRITE_DATA_NUM)
            reset_target_bytes = struct.pack('<' + str(len(reset_target_bytes)) + 'sH',
                                             reset_target_bytes,
                                             self.RESET_BRD_CRC_RESULT)
            self.forwardwrite(reset_target_bytes)
            dataque = bytearray(b'')
            while len(dataque) < 8:
                byteback = self._chardev.read(1)
                if byteback is b'':
                    break
                else:
                    dataque += byteback
            if len(dataque) == 0:
                print('reset target board timeout')
                continue
            elif dataque[0] is 0x1f:
                print('board in bootloader')
                return
            elif dataque == bytearray(reset_target_bytes):
                print('reset success')
                return
            else:
                print(dataque)

    def forwardwrite(self, data):
        pack = struct.pack('<I' + str(len(data)) + 's',
                           self.SONICIAP_PACKHEAD, data)
        self._chardev.ioctl("clearReadBuf")
        self._chardev.write(pack)
