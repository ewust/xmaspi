#!/usr/bin/python


import time
import sys

NUM_STRANDS=1

def send_pkt(addr, brightness, green, blue, red, strand=0):
    f = open('/dev/xmas', 'w')
    f.write(chr((strand << 6) | addr) + chr(brightness) + chr(green) + chr(blue) + chr(red))
    f.close()

#initialize
def init_lights(strand=0):
    for addr in range(50):
        send_pkt(addr, 0, 0, 0, 0, strand)



for s in range(NUM_STRANDS):
    init_lights(s)




class RGBStrands(object):

    def __init__(self):
        # brightness, green, blue, red
        self.lights = [(0, 0, 0, 0)]*(50*NUM_STRANDS)

    def update_pattern(self):
        addr = 0
        strand = 0
        for x in self.lights:
            send_pkt(addr, x[0], x[1], x[2], x[3], strand)
            
            addr += 1
            if addr == 50:
                addr = 0
                strand += 1



    
class BinaryShifter(RGBStrands):

    def __init__(self, text=""):
        super(BinaryShifter, self).__init__()
        self.update_text(text)
    

    def update_text(self, text):
        self.text = text
        self.bit_offset = -len(self.lights) 


    def update_pattern(self):
        pos = 0
        for c in self.text:
            for bit in range(8):
                index = pos - self.bit_offset
                if index >= 0 and index < len(self.lights):
                    if ord(c) & (1 << (7-bit)):
                        # 1 (maize)
                        self.lights[index] = (200, 0, 15, 15)
                    else:
                        # 0 (blue)
                        self.lights[index] = (200, 15, 0, 0)

                pos += 1
            index = pos - self.bit_offset 
            if index >= 0 and index < len(self.lights):
                self.lights[index] = (0, 0, 0, 0)

            pos += 1
                
        # fill rest with off
        index += 1
        while index < len(self.lights):
            self.lights[index] = (0, 0, 0, 0)
            index += 1


        super(BinaryShifter, self).update_pattern()

    def shift(self, num_spaces=1):
        self.bit_offset += num_spaces
        if self.bit_offset >= len(self.text)*8:
            self.bit_offset %= (len(self.text)*8)
            self.bit_offset -= len(self.lights)
            self.lights[0] = (0, 0, 0, 0)

        


s = sys.stdin.read()
bs = BinaryShifter(s)
while True:
    bs.update_pattern()
    bs.shift()
    time.sleep(1)




