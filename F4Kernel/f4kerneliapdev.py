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
		
		print("set Target Board Boot")
		if self.checktargetboardinbootloader():
			return

		print('Set F4Kernel to bootloader')
		GET_APP_VERSION_CMD = 0x1032
		SET_TO_BOOTLOADER_CMD = 0x101D

		QUERY_APP_VERSION_MSG = struct.pack(
			'<2I', GET_APP_VERSION_CMD, 0xffffffff)
		JUMP_TO_BL_MSG = struct.pack('<2I', SET_TO_BOOTLOADER_CMD, 0xffffffff)

		# confirm current firmware version
		ReadTimeoutCnt = 0
		wbb = whileBreaker(3)
		while True:
			self._chardev.ioctl("usePrimeAddress")
			self._chardev.write(QUERY_APP_VERSION_MSG)
			backParamNum = 4
			versionrawmsg = self._chardev.read(backParamNum * 4)

			if(len(versionrawmsg) != backParamNum * 4):
				print('invalid back message: %s' % versionrawmsg)
				if(ReadTimeoutCnt < 4):
					ReadTimeoutCnt = ReadTimeoutCnt + 1
					continue
				else:
					return 0x01

			(head, v0, v1, v2) = struct.unpack('<4I', versionrawmsg)

			if(head != GET_APP_VERSION_CMD):
				print('pack head error: 0x%X' % head)
				wbb()
				continue

			print('Get app version: %d.%d.%d' % (v0, v1, v2))

			if(v0 > 1):
				print('APP Version confirm ok!')
				break
			elif(v1 > 7):
				print('APP Version confirm ok!')
				break
			elif(v2 >= 906):
				print('APP Version confirm ok!')
				break

			print('App version do not support auto update, press enter to exit...')
			input()
			quit()

		wb = whileBreaker(2)
		wbb = whileBreaker(3)
		self._chardev.write(JUMP_TO_BL_MSG)
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
		print("check target board 1")
		self._chardev.ioctl("useSeconAddress")
		self._chardev.ioctl("clearReadBuf")
		self._chardev.write(b'\x00' * 20)
		prevTimeout = [0.1]
		self._chardev.ioctl('getReadTimeout', prevTimeout)
		self._chardev.ioctl('readTimeout', 0.01)
		print("check target board 2")
		try:
			stmback = self._chardev.read(4)
			self._chardev.ioctl('readTimeout', prevTimeout[0])
		except ConnectionResetError:
			print('Remote port closed, may not in bootloader')
			return False
			

		for b in stmback:
			if b != CIapDev.ACK[0] and b != CIapDev.NACK[0]:
				print('stmback = ' + str(stmback) + 'Not in bootloader!')
				return False
		
		if 0 == len(stmback):
			print('No repley, not in bootloader')
			return False

		print('Already in bootloader!')
		return True

	def checkapplicationversion(self, version):		
		
		if self.checktargetboardinbootloader():
			return

		GET_APP_VERSION_CMD = 0x1032
		SET_TO_BOOTLOADER_CMD = 0x101D

		QUERY_APP_VERSION_MSG = struct.pack(
			'<2I', GET_APP_VERSION_CMD, 0xffffffff)

		wb = whileBreaker(4)
		wbb = whileBreaker(5)
		# confirm current firmware version
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

			if(v0 > version[0]):
				print('Version confirm ok!')
				break
			elif(v1 > version[1]):
				print('Version confirm ok!')
				break
			elif(v2 >= version[2]):
				print('Version confirm ok!')
				break

			print('App version do not support auto update, press enter to exit...')
			input()
			quit()

class CheckWhichBox(object):

    def __init__(self, chardevice):
        self.__cd = chardevice
        GET_APP_VERSION_CMD = 0x1032
        self.QUERY_APP_VERSION_MSG = struct.pack('<2I', GET_APP_VERSION_CMD, 0xffffffff)
        self.backParamNum = 5
        self.is_old_version = False

    def transferQueryData(self):
        wb = whileBreaker(7,5)
        while True:
            self.__cd.write(self.QUERY_APP_VERSION_MSG)
            self.versionrawmsg = self.__cd.read(self.backParamNum * 4)
            if(len(self.versionrawmsg) != self.backParamNum * 4):
                # compatible with old version
                self.oldversionrawmsg = self.__cd.read(4 * 4)
                if (len(self.oldversionrawmsg) == 16):   
                    self.is_old_version = True
                    break
                print('invalid back message: %s' % self.versionrawmsg)
                self.__cd.clearReadBuf()
                wb()
                continue
            (self.head, self.v0, self.v1, self.v2, self.box) = struct.unpack('<5I', self.versionrawmsg)
            break

    def isSRC2000(self):
        self.transferQueryData()
        if(self.is_old_version):
            print('old version, old logic...')
            return True  
        elif(2 == int(chr(self.box))):
            return True
        else:
            print('pack box error: 0x%X' % self.box)
            return False
            

    def isSRC1100(self):
        self.transferQueryData()
        if(self.is_old_version):
            print('old version, old logic...')
            return True
        elif(1 == int(chr(self.box))):
            return True 
        else:
            print('pack box error: 0x%X' % self.box)
            return False
            