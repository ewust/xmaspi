#!/usr/bin/python

import sys

def send_pkt(addr, brightness, green, blue, red, strand=0):
    f = open('/dev/xmas', 'w')
    f.write(chr((strand << 6) | addr) + chr(brightness) + chr(green) + chr(blue) + chr(red))
    f.close()

#initialize


brightness = int(sys.argv[1])
b = int(sys.argv[2])
g = int(sys.argv[3])
r = int(sys.argv[4])

strand = 0
if len(sys.argv) > 5:
    strand = int(sys.argv[5])


for i in range(50):
    send_pkt(i, 0, 0, 0, 0, strand)


for i in range(50):
    send_pkt(i, brightness, b, g, r, strand)
