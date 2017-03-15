import threading
import sys
import signal

from time import sleep
from iapIntf import CIapDev
from charDev import CCharDev, CUdpCharDev

flashMap_F4 = [0x08000000, 0x0800c000, 0x08010000]
udpCharDev = CUdpCharDev(('192.168.192.4',5003), ('192.168.192.4',19204))
# udpCharDev = CUdpCharDev(('127.0.0.1', 9999),('127.0.0.1', 9999))
udpIapDev = CIapDev(udpCharDev, flashMap_F4)

def runReceiver():
    sys.exit()

def task():
    udpIapDev.jumpToBootloader()
    ver = udpIapDev.getBootLoaderVersion()
    # print('version: 0x%02X'%ver)
    udpIapDev.loadBin('Project.bin')
    # udpIapDev.writeBootParam(CIapDev.byteBootParam_APP)
    udpIapDev.jumpToApp()
    # udpIapDev.resetBoard()
    sys.exit()

def quit(signum, frame):
    sys.exit()

try:
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    t1 = threading.Thread(target = runReceiver)
    t1.setDaemon(True)

    t2 = threading.Thread(target = task)
    t2.setDaemon(True)

    # t1.start()
    t2.start()

    while True:
        pass
except Exception as exc:
    print(exc)




