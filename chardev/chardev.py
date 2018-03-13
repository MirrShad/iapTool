from abc import ABCMeta, abstractmethod
import sys

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


class whileBreaker(object):
    
    def __init__(self, code, timeout = 10):
        self.__code = code
        self.__timeout = timeout if timeout > 0 else 0
        self.__count = 0

    def __call__(self):
        self.__count += 1
        # print(self.__count)
        if self.__count > self.__timeout:
            print("process failed, exit %d" % self.__code)
            sys.exit(self.__code)