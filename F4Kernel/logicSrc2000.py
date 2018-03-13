import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import json

from time import sleep
from chardev.udpchardev import UdpCharDev
from F4Kernel.f4kerneliapdev import CF4KernelIapDev

try:
    with open('..\\User\\ipconfig.json', 'r') as f:
        data = json.load(f)
        f.close()
    F4K_ip = data['inet addr']

except:
    F4K_ip = '192.168.192.4'
    # F4K_ip = '127.0.0.1'

if(2 == len(sys.argv)):
    bin_file = sys.argv[1]
    #*.gyro.bin
    tail2 = bin_file[-8:-4]
    if tail2 != '.sc2':
        print('not the firmware for seer controller, press enter to continue...')
        sleep(2)
        sys.exit(1)
else:
    bin_file = '../Output/Project.bin'

BOOTLOADER_START_ADDR = 0x08000000
BOOTPARAM_ADDR = 0x0800C000
APP_START_ADDR = 0x08010000
chardev = UdpCharDev((F4K_ip, 15003), (F4K_ip, 5000))
udpIapDev = CF4KernelIapDev(chardev)
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
