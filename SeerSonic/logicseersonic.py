import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import json
# os.chdir(sys.path[0])

from time import sleep
from SeerSonic.seersoniciapdev import CSeerSonicIapDev
from chardev.udpchardev import UdpCharDev

try:
    with open('..\\User\\ipconfig.json', 'r') as f:
        data = json.load(f)
        f.close()
    F4K_ip = data['inet addr']

except:
    F4K_ip = '192.168.192.4'

if(2 == len(sys.argv)):
    bin_file = sys.argv[1]
    #*.gyro.bin
    tail2 = bin_file[-7:-4]
    if tail2 != '.ss':
        print('not the firmware for seer controller, press enter to continue...')
        sleep(2)
        sys.exit(1)
else:
    bin_file = '../Output/Project.bin'

BOOTLOADER_START_ADDR = 0x08000000
BOOTPARAM_ADDR = 0x08007800
APP_START_ADDR = 0x08008000
chardev = UdpCharDev((F4K_ip, 15003), (F4K_ip, 15003))
udpIapDev = CSeerSonicIapDev(chardev)
udpIapDev.setforwardmode()
udpIapDev.settargetboardbootloader()
FWV = udpIapDev.getbootloaderversion()
print('firmware version V%X.%X' % (FWV >> 4, FWV & 0xF))
udpIapDev.loadbin(bin_file, APP_START_ADDR)
udpIapDev.loaduint32(0xaaaa5555, BOOTPARAM_ADDR)
udpIapDev.jumpToAddress(APP_START_ADDR)
udpIapDev.resetforwardmode()

sleep(1)
# os.system('pause')
sys.exit(0)
