import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import time
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

def read():
    BOOTLOADER_START_ADDR = 0x08000000
    BOOTPARAM_ADDR = 0x0800C000
    IAP_UDP_PORT = 5000
    APP_START_ADDR = 0x08010000

    chardev = UdpCharDev((F4K_ip, 15003), (F4K_ip, IAP_UDP_PORT))
    udpIapDev = CF4KernelIapDev(chardev)
    udpIapDev.settargetboardbootloader()
    FWV = udpIapDev.getbootloaderversion()
    if(FWV == 0x01):
        return 0x01
    udpIapDev.readbin(time.strftime('SRC1100%Y%m%d-%H_%M_%S')+'_readback.sc.bin',APP_START_ADDR)
    udpIapDev.restorebootparam(BOOTPARAM_ADDR)
    udpIapDev.jumpToAddress(APP_START_ADDR)
    udpIapDev.resetforwardmode()
    time.sleep(1)
    sys.exit(0)
