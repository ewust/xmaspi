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
for i in range(NUM_BULBS):
    strand.set_bulb_color(colors[i][0], colors[i][1], colors[i][2])

strand.set_strand_brightness(200)
