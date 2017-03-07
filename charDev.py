import sys
import time
from abc import ABCMeta, abstractmethod

class CCharDev(object):
    __metaclass__ = ABCMeta

    _dataQue = []
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def write(self, charflow):
        pass
    
    @abstractmethod
    def read(self, len):
        pass

    @abstractmethod
    def run(self):
        pass

    def clearReadBuf(self):
        self._dataQue.clear()
    
import socket
class CUdpCharDev(CCharDev):
    def __init__(self, address = ('192.168.1.4',5003)):
        print('init target IP:%s, port:%d'%(address[0], address[1]))
        self._address = address
        self._so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._readTimeout = 10
    
    def open(self):
        pass
    
    def close(self):
        self._so.close()

    def write(self, data):
        self._so.sendto(data, self._address)

    def read(self, bufflen):
        count = 0
        while(True):
            if(len(self._dataQue) >= bufflen):
                ret = self._dataQue[0:bufflen]
                self._dataQue[0:bufflen] = b''
                return bytearray(ret)
            if(count > self._readTimeout):
                return b''
            count += 0.1
            time.sleep(0.1)

    def run(self):
        self._so.settimeout(0.1)
        data = b''
        try:
            data = self._so.recvfrom(100)[0]
        except socket.timeout:
            pass
        if(len(data) > 0):
            self._dataQue += data
        
    def setReadtimeout(self, nSec:"in seconds"):
        self._readTimeout = nSec

# import time
# testUdp = CUdpCharDev(('127.0.0.1',5003))
# for i in range(0, 30):
#     time.sleep(1)
#     testUdp.run()
#     print(testUdp.read(3))