import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import json

from time import sleep
from chardev.udpchardev import UdpCharDev
from F4Kernel.f4kerneliapdev import CF4KernelIapDev

IAP_UDP_PORT = 5000

BOOTLOADER_START_ADDR = 0x08000000
BOOTPARAM_ADDR = 0x0800C000
APP_START_ADDR = 0x08020000
bootApp = ''

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

    if(tail2 == 'scb'):
        IAP_UDP_PORT = 5000
        APP_START_ADDR = 0x08010000
        bootApp = 'SRC1100_bootApp_v1.5.scba.bin'
        print('firmware for SRC1100, IAP port: %d'%IAP_UDP_PORT)
    elif (tail2 == 'scb2'):
        IAP_UDP_PORT = 6000
        APP_START_ADDR = 0x08020000
        bootApp = 'SRC2000_bootApp_v1.4.scba.bin'
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

chardev = UdpCharDev((F4K_ip, 15003), (F4K_ip, IAP_UDP_PORT))
udpIapDev = CF4KernelIapDev(chardev)
udpIapDev.settargetboardbootloader()
FWV = udpIapDev.getbootloaderversion()
if(FWV == 0x01):
    sys.exit(0)
print('bootloader version V%X.%X' % (FWV >> 4, FWV & 0xF))

sleep(5)

# readback firmware
print('read back the firmware')
backupBin = 'readback.bin'
udpIapDev.readbin(backupBin, APP_START_ADDR)


# write bootloader to APP_START_ADDR
print('download the boot app')
udpIapDev.loadbin(bootApp, APP_START_ADDR)
udpIapDev.restorebootparam(BOOTPARAM_ADDR)
udpIapDev.jumpToAddress(APP_START_ADDR)

sleep(10)

# write bootloader
print('write the new bootloader')
BAV = udpIapDev.getbootloaderversion()
if(BAV == 0x01):
    sys.exit(0)
print('boot app version V%X.%X' % (BAV >> 4, BAV & 0xF))

sleep(2)

udpIapDev.loadbin(bin_file, BOOTLOADER_START_ADDR)
udpIapDev.setInBL(BOOTPARAM_ADDR)
udpIapDev.jumpToAddress(BOOTLOADER_START_ADDR)

sleep(2)

# load the readback firmware to f4k
udpIapDev.loadbin(backupBin, APP_START_ADDR)
udpIapDev.restorebootparam(BOOTPARAM_ADDR)
udpIapDev.jumpToAddress(APP_START_ADDR)
udpIapDev.resetforwardmode()


sleep(1)
# os.system('pause')
sys.exit(0)
