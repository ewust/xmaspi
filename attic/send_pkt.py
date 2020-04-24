#!/usr/bin/python


import sys


def send_pkt(addr, brightness, green, blue, red):
    f = open('/dev/xmas', 'w')
    f.write(chr(addr) + chr(brightness) + chr(green) + chr(blue) + chr(red))
    f.close()



send_pkt(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
