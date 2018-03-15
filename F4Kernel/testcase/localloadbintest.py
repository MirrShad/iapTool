import sys
sys.path.append('../')
sys.path.append('../../')

import os
import json

from time import sleep
from chardev.udpchardev import UdpCharDev
from F4Kernel.f4kerneliapdev import CF4KernelIapDev
import subprocess
import platform

F4K_ip = '127.0.0.1'
IAP_UDP_PORT = 5000

scriptpath = '..\\..\\iapToolTest\\f4kernaltest_boost\\'
if('Windows' == platform.system()):
    os.system(scriptpath + 'build.bat')
    subprocess.Popen([scriptpath + 'test.bat'], creationflags=subprocess.CREATE_NEW_CONSOLE)
elif('Linux' == platform.system()):
    scriptpath = scriptpath.replace('\\', '/')
    os.system(scriptpath + 'build.sh')
    subprocess.Popen(['sh', scriptpath + 'test.sh'])
else:
    print('Unknow platfrom: ' + platform.system())
    sys.exit(-1)

sleep(1)

if(2 == len(sys.argv)):
    bin_file = sys.argv[1]

    (tail2, tail) = bin_file.split('.')[-2:]
    if(tail != 'bin'):
        print('firmware should be *.bin, but current: ' + tail)
        sleep(2)
        sys.exit(1)

    if(tail2 == 'sc'):
        IAP_UDP_PORT = 5000
        print('firmware for SRC1100, IAP port: %d'%IAP_UDP_PORT)
    elif (tail2 == 'sc2'):
        IAP_UDP_PORT = 6000
        print('firmware for SRC1100, IAP port: %d'%IAP_UDP_PORT)
    else:
        print('unknow firmware type, should be *.sc.bin or *.sc2.bin, current: ' + tail2)
        sleep(2)
        sys.exit(1)

BOOTLOADER_START_ADDR = 0x08000000
BOOTPARAM_ADDR = 0x0800C000
APP_START_ADDR = 0x08010000
chardev = UdpCharDev((F4K_ip, 15003), (F4K_ip, IAP_UDP_PORT))
udpIapDev = CF4KernelIapDev(chardev)
udpIapDev.settargetboardbootloader()
FWV = udpIapDev.getbootloaderversion()
print('firmware version V%X.%X' % (FWV >> 4, FWV & 0xF))
udpIapDev.loadbin(bin_file, APP_START_ADDR)
udpIapDev.restorebootparam(BOOTPARAM_ADDR)
udpIapDev.readbin('readback.bin', APP_START_ADDR)
udpIapDev.jumpToAddress(APP_START_ADDR)
udpIapDev.resetforwardmode()

print('Test finished...')
sys.exit()
