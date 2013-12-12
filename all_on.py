#!/usr/bin/python

import sys
f = open('/dev/xmas', 'w')

def send_pkt(addr, brightness, green, blue, red, strand=0):
    global f
    f.write(chr((strand << 6) | addr) + chr(brightness) + chr(green) + chr(blue) + chr(red))

#initialize


brightness = int(sys.argv[1])
r = int(sys.argv[2])
g = int(sys.argv[3])
b = int(sys.argv[4])

for i in range(50):
    send_pkt(i, 0, 0, 0, 0, 0)
    send_pkt(i, 0, 0, 0, 0, 1)


for i in range(50):
    send_pkt(i, brightness, b, g, r, 0)
    send_pkt(i, brightness, b, g, r, 1)

f.close()
