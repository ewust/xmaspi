xmaspi network service
======================

Drive your RGB Christmas lights from UDP or TCP

Requires `/dev/xmas` and libevent2.

It is super cool!

Build
-----

To compile, you'll need:
    
    `apt install libevent-dev`

Then run `make` to build both `udp-driver` and `tcp-driver`.

Run
---

Both listen on port 1337 for frames of 100 bulbs, each 4 bytes:
brightness, red, green, blue. Only the bulbs that changed are sent to
the lights; if frames arrive faster than the lights can update, the
older ones are skipped.

Options:

    -v        print frames/sec and bulbs/sec once a second
    -p PORT   listen on PORT instead of 1337

