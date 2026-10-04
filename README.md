xmaspi
======

This code runs on a Raspberry Pi and drives the [Bob and Betty Beyster Blinkenlights](https://docs.google.com/document/d/1kO2LvbGgDD-2SHmxqKJG2VrXhhx4hQG96N9LBkynDJc/edit?tab=t.0), a programmable light installation that consists of a pair of [GE Color Effects G-35 LED strands](https://web.archive.org/web/20190322170653/http://www.deepdarc.com/2010/11/27/hacking-christmas-lights/) with 50 bulbs each. Clients control the lights over the network by sending frames that each specify the state of every bulb.

Hardware
--------

The data lines of the two strands connect to GPIO 17 and 18. The strands share a power supply with the Pi, so they power up together. The deployed Pi runs Raspbian 10 (Buster).

How it fits together
--------------------

- **[lkm/](lkm/)** is a kernel module that bit-bangs the G-35 protocol on the GPIOs and exposes `/dev/xmas`. At load, it turns all bulbs off and assigns each bulb its address. It updates both strands simultaneously, so a full update takes about 41 ms (~24 Hz).
- **[driver/](driver/)** contains `udp-driver` and `tcp-driver`, which listen on port 1337 for 400-byte frames: one 4-byte word per bulb (brightness, red, green, blue), for bulbs 0–99 in order. Each frame is diffed against the current state, and only changed bulbs are sent to `/dev/xmas`.
- **[stream-client.py](stream-client.py)** connects to blinken.org's WebSocket stream (`wss://blinken.org/api/0/stream`) and relays each frame to `udp-driver` on localhost, reconnecting whenever the connection drops. Because the Pi connects out to the server, it works behind NAT and doesn't depend on the server knowing the Pi's address.
- **[driver.py](driver.py)** is a Python interface to `/dev/xmas` that maps bulbs 0–99 to strands and addresses. Run it with no arguments to play a test pattern, as `driver.py LED BRIGHTNESS RED GREEN BLUE` to set one bulb, or as `driver.py --set-all BRIGHTNESS RED GREEN BLUE` to set them all.
- **[startup.sh](startup.sh)** runs at boot and starts everything: it loads the module, plays the test pattern, starts `udp-driver` and `stream-client.py`, then runs **[network.sh](network.sh)**, a watchdog that checks in with blinken.org, blinks the lights red while the network is down, and reboots if it doesn't come back.

Brightness ranges from 0 to 255; colors range from 0 to 15. Bulb 0 is at the far end of the first strand, and bulb 99 at the far end of the second.

Setup
-----

    sudo apt install raspberrypi-kernel-headers libevent-dev python3-websocket
    make -C lkm
    make -C driver
    sudo ./startup.sh

See [lkm/README.md](lkm/README.md) and [driver/README.md](driver/README.md) for details. [attic/](attic/) holds older incarnations that are no longer maintained but are kept around for sentimental and archaeological reasons.
