#!/usr/bin/python


import time
import sys
import driver


class RGBStrands(object):

    def __init__(self):
        # brightness, green, blue, red
        self.driver = driver.Driver()
        self.lights = [(0, 0, 0, 0)]*(50*self.driver.num_strands)

    def update_pattern(self):
        addr = 0
        strand = 0
        for x in self.lights:
            #driver.Driver().write_led(addr, x[0], x[1], x[2], x[3]) 
            self.driver.write_led(addr, x[0], x[1], x[2], x[3]) 
            addr += 1

        #driver.Driver().flush_buffer()

    
class BinaryShifter(RGBStrands):

    def __init__(self, text=""):
        super(BinaryShifter, self).__init__()
        self.update_text(text)
    

    def update_text(self, text):
        self.text = text
        self.bit_offset = -len(self.lights) 


    def update_pattern(self):
        pos = 0
        index = pos - self.bit_offset
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
        if self.bit_offset >= len(self.text)*9:
            self.bit_offset %= (len(self.text)*8)
            self.bit_offset -= len(self.lights)
            self.lights[0] = (0, 0, 0, 0)
            return False
        return True


if __name__=="__main__":
    d = driver.Driver()
    s = sys.stdin.read()
    bs = BinaryShifter(s)
    while True:
        bs.update_pattern()
        bs.shift()
        time.sleep(.1) 

