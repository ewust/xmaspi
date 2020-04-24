#!/usr/bin/python


import time
import random


def send_pkt(addr, brightness, green, blue, red):
    f = open('/dev/xmas', 'w')
    f.write(chr(addr) + chr(brightness) + chr(green) + chr(blue) + chr(red))
    f.close()

for addr in range(50):
    send_pkt(addr, 0, 0, 0, 0)



def randomize_colors(brightness=0x00):
    for addr in range(50):
        send_pkt(addr, brightness, random.randint(0, 13), random.randint(0, 13), random.randint(0, 13))

randomize_colors()


while True:
    randomize_colors(0xcc)
    time.sleep(0.01)


brightness = 1
direction = 1
while True:
    send_pkt(63, brightness, 13, 13, 13)
    brightness += direction
    if (brightness % 10 == 0):
        #print brightness
        pass
    if (brightness > 200):
        brightness -= 1
        direction = -1
    elif brightness == 0:
        randomize_colors()
        brightness = 1
        direction = 1

    #time.sleep(0.0)



