# SRC IAP Tools
Robot controller In Application program tools.

# Table of Contents

   * [Requirements](#Requirements)
   * [Char Device](#char-device)
      * [UDP Char Device](#udp-char-device)
    * [IAP Device](#iap-device)
   * [Basic Test Case](#basic-test-case)
   * [F4Kernel](#yaw-comparer)
   * [SeerGyro](#seergyro)
   * [SeerSonic](#seersonic)
   * [Subsystem](#subsystem)

# Requirements

- Python 3.6.x

# Char Device
All the char stream device can be abstracted as a chardev.
For example, UDP, TCP, CAN, UART, SPI, etc.
Methods in CharDev are shown as follow:
   * open()
   * close()
   * write()
   * read()
   * ioctl()

## UDP Char Device


# IAP Device
There is an abstract base class for IAP Device.
Methods in IapDevice are shown as follow:
   * jumptoaddr(addr)
   * getbootloaderversion()
   * loadbin(filename, addr)
   * readbin(filename, addr)
   * readuint32(valueaddr, value)
   * loaduint32(blockstartaddr, valueaddr, value)
   * confirmack()
   * forwardwrite(bytes)
   * restorebootoption(blockstartaddr)

And some static methods:
   * getxor(bytes)
   * getbytesfromuint32(bytes)
   * isallbytes0xff(bytes)

And some other methods that related with second class device:
   * setforwardmode()
   * exitforwardmode()
   * settargetboardtobootloader()
   * resettargetboard()

# Basic Test Case
Base function test, including:
1. jumptest. Set target board to bootloader and jump back to application layer.
2. readtest. Read code from target board and jump back to application layer.

# F4Kernel
compile cmd: pyinstaller -p ..\iapdev -p ..\chardev -F logicf4kernel.py

# SeerGyro

# Subsystem
