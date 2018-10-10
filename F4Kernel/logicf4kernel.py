import os
import sys

if(1 == len(sys.argv)):
    import readf4kernel1100
    if(readf4kernel1100.read() == 0x01):
        import readf4kernel2000
        print("not read from SRC1100")
        readf4kernel2000.read()
elif(2 == len(sys.argv)):
    import loadf4kernel
    loadf4kernel.load(sys.argv)
else:
    print("error number of input")
