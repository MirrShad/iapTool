import sys
from abc import ABCMeta, abstractmethod

class CCharDev(object):
    __metaclass__ = ABCMeta

    _dataQue = bytearray(b'')
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
        self._dataQue = b''
    
import socket
class CUdpCharDev(CCharDev):
    def __init__(self, address = ('192.168.1.4',5003)):
        print('init target IP:%s, port:%d'%(address[0], address[1]))
        self._address = address
        self._so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def open(self):
        pass
    
    def close(self):
        self._so.close()

    def write(self, data):
        self._so.sendto(data, self._address)

    def read(self, len):
        ret = self._dataQue[0:len]
        self._dataQue[0:len] = []
        return ret

    def run(self):
        self._so.settimeout(0.1)
        data = b''
        try:
            data = self._so.recvfrom(100)[0]
        except socket.timeout:
            pass
        if(len(data) > 0):
            self._dataQue += bytearray(data)
        
# import time
# testUdp = CUdpCharDev(('127.0.0.1',5003))
# for i in range(0, 30):
#     time.sleep(1)
#     testUdp.run()
#     print(testUdp.read(3))