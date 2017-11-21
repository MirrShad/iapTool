import sys
import time
import os
from abc import ABCMeta, abstractmethod


class CCharDev(object):
    __metaclass__ = ABCMeta

    _dataQue = bytearray(b'')
    _latestCharDevVersion = 0x14

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
    def ioctl(self, cmd, arg):
        pass

    def clearReadBuf(self):
        self._dataQue.clear()
