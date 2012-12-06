#!/usr/bin/python

from multiprocessing import Process, Lock

import time
import rgb_strand

NUM_BULBS = 100

def func(lock):
    colors = [(15, 0, 0), \
            (15, 3, 0), \
            (15, 15, 0), \
            (0,   15,   0), \
            (0,   0, 15), \
            (4,  14, 13), \
            (14, 0, 14) ]

    strand = rgb_strand.RGBStrand(NUM_BULBS)
    strand.set_strand_pattern(colors)
    strand.set_strand_brightness(200)

    i = 0
    while True:
        strand.push_top(200, colors[idx][0], colors[idx][1], colors[idx][2])
        i += 1
        i %= len(colors)

        # Let other people use it if they want it
        lock.release()
        lock.acquire()




if __name__=="__main__":
    func(Lock())

