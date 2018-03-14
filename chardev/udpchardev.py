import socket
import os
import sys
from .chardev import CCharDev


class UdpCharDev(CCharDev):

    def __init__(self, primeAddress, seconAddress):
        # primeAddress: ip+port for command jump to bootloader
        self._primeAddress = primeAddress
        # address: ip+port for IAP operation
        self._seconAddress = seconAddress
        # address: abstructed ip+port
        self._address = self._seconAddress
        self._so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('init target IP:%s, port:%d' %
              (self._address[0], self._address[1]))
        self._so.settimeout(1)
        try:
            self._so.sendto(b'', self._primeAddress)
        except:
            pass

    def open(self):
        pass

    def close(self):
        self._so.close()

    def write(self, data):
        self._so.sendto(data, self._address)

    def read(self, bufflen):
        while(True):
            if(len(self._dataQue) >= bufflen):
                ret = self._dataQue[0:bufflen]
                self._dataQue[0:bufflen] = b''
                return ret
            else:
                try:
                    self._dataQue += self._so.recvfrom(1024)[0]
                except socket.timeout:
                    print('readtimeout, expect %d bytes, get %d bytes' %
                          (bufflen, len(self._dataQue)))
                    return b''
                except ConnectionResetError:
                    print('Connection was closed by remote host')
                    print('It\'s most likely that you use a SRC1100 firmware to flash SRC2000')
                    sys.exit(1)

    def ioctl(self, cmd, arg=0):
        if(cmd == "usePrimeAddress"):
            self._address = self._primeAddress
        elif(cmd == "useSeconAddress"):
            self._address = self._seconAddress
        elif (cmd == "readTimeout"):
            self._so.settimeout(arg)
        elif (cmd == "getReadTimeout"):
            arg[0] = self._so.gettimeout()
        elif (cmd == "clearReadBuf"):
            prevTimeout = [0.1]
            self.ioctl('getReadTimeout', prevTimeout)
            self._dataQue.clear()
            self._so.settimeout(0)
            while(True):
                try:
                    self._so.recvfrom(1000)
                except BlockingIOError:
                    break
            self._so.settimeout(prevTimeout[0])

        elif(cmd == "latestVersion"):
            arg[0] = self._latestCharDevVersion

        else:
            print("unknow param!")
            os.system("pause")
            quit()
