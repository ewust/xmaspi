#!/usr/bin/python

colors = [(255, 0, 0), \
(255, 165, 0), \
(255, 255, 0), \
(0,   0,   255), \
(0,   128, 0), \
(64,  224, 208), \
(238, 130, 238) ]

import rgb_strand

NUM_BULBS = 100

strand = rgb_strand.RGBStrand(NUM_BULBS)
strand.set_strand_pattern(colors)
strand.set_strand_brightness(200)
