import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import json

from time import sleep
from chardev.udpchardev import UdpCharDev
from F4Kernel.f4kerneliapdev import CF4KernelIapDev

IAP_UDP_PORT = 5000

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
        print('firmware for SRC2000, IAP port: %d'%IAP_UDP_PORT)
    else:
        print('unknow firmware type, should be *.sc.bin or *.sc2.bin, current: ' + tail2)
        sleep(2)
        sys.exit(1)

    # tail2 = bin_file[-8:-4]
    # if tail2 != '.sc2':
    #     print('not the firmware for seer controller, press enter to continue...')
    #     sleep(2)
    #     sys.exit(1)
else:
    print('invalid arguments, example: logic.exe ./src1100_1.7.901_2018.sc.bin')

BOOTLOADER_START_ADDR = 0x08000000
BOOTPARAM_ADDR = 0x080FC000
APP_START_ADDR = 0x08020000
chardev = UdpCharDev((F4K_ip, 15003), (F4K_ip, IAP_UDP_PORT))
udpIapDev = CF4KernelIapDev(chardev)
print("sssssssssssssssssssssssssssss")
udpIapDev.settargetboardbootloader()
print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
FWV = udpIapDev.getbootloaderversion()
print('firmware version V%X.%X' % (FWV >> 4, FWV & 0xF))
udpIapDev.loadbin(bin_file, APP_START_ADDR)
print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
udpIapDev.restorebootparam(BOOTPARAM_ADDR)
udpIapDev.jumpToAddress(APP_START_ADDR)
udpIapDev.resetforwardmode()

sleep(1)
# os.system('pause')
sys.exit(0)
