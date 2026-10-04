xmaspi kernel module
====================

RGB Christmas lights Loadable Kernel Module for RaspberryPi

It is super cool!

Build
-----

To compile, you'll need:
    
    `apt install raspberrypi-kernel-headers`

Install
-------

Run `setup.sh` to load the module, which creates `/dev/xmas`.

Strands are driven from GPIO 17 and 18 by default. To use other pins:

    ./setup.sh strand0_gpio=22 strand1_gpio=23

At load, the module turns all bulbs off and numbers the bulbs on each
strand 0-49, starting from the end nearest the Pi. Bulbs only accept a
new address right after power-up, so load the module before anything
else writes to the strands.

Write 5-byte frames to `/dev/xmas`: strand bit (0x40) | bulb address,
brightness, blue, green, red. Frames for both strands in the same write
are sent simultaneously.
