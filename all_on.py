#!/usr/bin/python



def send_pkt(addr, brightness, green, blue, red, strand=0):
    f = open('/dev/xmas', 'w')
    f.write(chr((strand << 6) | addr) + chr(brightness) + chr(green) + chr(blue) + chr(red))
    f.close()

#initialize
for i in range(50):
    send_pkt(i, 0, 0, 0, 0)

for i in range(50):
    send_pkt(i, 0xcc, 13, 13, 13)
