import sys
sys.path.append('../')

import os
import json

from time import sleep
from SeerGyro.seergyroiapdev import CSeerGyroIapDev
from chardev.udpchardev import UdpCharDev
from F4Kernel.f4kerneliapdev import CF4KernelIapDev, CheckWhichBox

try:
    with open('..\\User\\ipconfig.json', 'r') as f:
        data = json.load(f)
        f.close()
    F4K_ip = data['inet addr']

except:
    F4K_ip = '192.168.192.4'

chardev = UdpCharDev((F4K_ip, 15003), (F4K_ip, 15003))
askwhichbox = CheckWhichBox(chardev)

if(2 == len(sys.argv)):
    bin_file = sys.argv[1]
    #*.gyro.bin 
    (tail2, tail) = bin_file.split('.')[-2:]
    if(tail != 'bin'):
        print('firmware should be *.bin, but current: ' + tail)
        sleep(2)
        sys.exit(1)

    if (tail2 == 'gy2') and (askwhichbox.isSRC2000()):
        pass
    elif (tail2 == 'gy') and (askwhichbox.isSRC1100()):
        pass
    else:
        print('not the firmware for seer gyro, press enter to continue...')
        sleep(2)
        sys.exit(1)
else:
    bin_file = '../Output/Project.bin'

BOOTLOADER_START_ADDR = 0x08000000
BOOTPARAM_ADDR = 0x0800FC00
APP_START_ADDR = 0x08005800

udpF4KIapDev = CF4KernelIapDev(chardev)
udpF4KIapDev.checkapplicationversion((1, 7, 906))
udpF4KIapDev.resetforwardmode()

udpIapDev = CSeerGyroIapDev(chardev)
udpIapDev.setforwardmode()
udpIapDev.settargetboardbootloader()
FWV = udpIapDev.getbootloaderversion()
print('firmware version V%X.%X' % (FWV >> 4, FWV & 0xF))
udpIapDev.loadbin(bin_file, APP_START_ADDR)
udpIapDev.restorebootparam(BOOTPARAM_ADDR)
udpIapDev.jumpToAddress(APP_START_ADDR)
udpIapDev.resetforwardmode()

sleep(1)
# os.system('pause')
sys.exit(0)
