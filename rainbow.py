#!/usr/bin/python

colors = [(15, 0, 0), \
(15, 3, 0), \
(15, 15, 0), \
(0,   15,   0), \
(0,   0, 15), \
(4,  14, 13), \
(14, 0, 14) ]

import time
import rgb_strand

NUM_BULBS = 100

strand = rgb_strand.RGBStrand(NUM_BULBS)
strand.set_strand_pattern(colors)
strand.set_strand_brightness(200)

while True:
    strand.scroll_forward()
    time.sleep(0.1)


