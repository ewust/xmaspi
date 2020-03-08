#!/usr/bin/python3

import sys

DRIVER='/dev/xmas'

def send_pkt(f, addr, brightness, green, blue, red, strand=0):
    f.write(bytes([(strand << 6) | addr, brightness, green, blue, red]))

def set_all(brightness, green, blue, red):
    with open(DRIVER, 'wb') as f:
        for i in range(50):
            send_pkt(f, i, brightness, b, g, r, 0)
            send_pkt(f, i, brightness, b, g, r, 1)
       	f.flush()

if __name__=="__main__":
    if len(sys.argv) < 4:
        print("usage: %s BRIGHTNESS R G B\n\nSets all bulbs to the specified condition." % sys.argv[0], file=sys.stderr)
        sys.exit(-1)

    brightness = int(sys.argv[1])
    r = int(sys.argv[2])
    g = int(sys.argv[3])
    b = int(sys.argv[4])

    set_all(0, 0, 0, 0)
    set_all(brightness, g, b, r)
