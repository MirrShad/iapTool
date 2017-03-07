import threading
import sys
from time import sleep
from iapIntf import CIapDev
from charDev import CCharDev, CUdpCharDev

flashMap_F4 = [0x08000000, 0x0800c000, 0x08010000]
# udpCharDev = CUdpCharDev(('192.168.1.4',5003))
udpCharDev = CUdpCharDev(('127.0.0.1', 9999))
udpCharDev.setReadtimeout(3)
udpIapDev = CIapDev(udpCharDev, flashMap_F4)

def runReceiver():
    while(True):
        udpIapDev.run()

def task():
    udpIapDev.jumpToBootloader()
    # udpIapDev.writeBootParam(CIapDev.byteBootParam_APP)
    # udpIapDev.jumpToApp()

t1 = threading.Thread(target = runReceiver)
t1.setDaemon(True)

t2 = threading.Thread(target = task)

t1.start()
t2.start()




