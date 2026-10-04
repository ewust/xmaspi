#!/usr/bin/env python3
"""Drive the Christmas lights through the /dev/xmas kernel driver.

LEDs are numbered 0 to NUM_LEDS - 1 across both strands; Driver maps
each LED to a (strand, bulb address) pair. The kernel module assigns
the bulb addresses when it loads, numbering each strand from the end
nearest the Pi.

Run with no arguments to play a test pattern, with
LED BRIGHTNESS RED GREEN BLUE to set a single LED, or with
--set-all BRIGHTNESS RED GREEN BLUE to set every LED.
"""

import argparse
import time
from typing import Dict, Sequence, Tuple, Union

DEVICE = '/dev/xmas'
STRAND_LEN = 50
NUM_STRANDS = 2
NUM_LEDS = STRAND_LEN * NUM_STRANDS

BROADCAST = -1          # LED ID that sets brightness on every bulb
BROADCAST_ADDR = 63     # Bulb address that every bulb listens to
MAX_BRIGHTNESS = 0xff   # The stock controller never exceeds 0xcc
MAX_COLOR = 0xf

PhysAddr = Tuple[int, int]  # (strand, bulb address)


def frame(phys_addr: PhysAddr, brightness: int,
          red: int, green: int, blue: int) -> bytes:
    """Encode one 5-byte /dev/xmas frame."""
    strand, addr = phys_addr
    if not 0 <= strand < NUM_STRANDS:
        raise ValueError(f'strand {strand} out of range')
    if not 0 <= addr <= BROADCAST_ADDR:
        raise ValueError(f'bulb address {addr} out of range')
    if not 0 <= brightness <= MAX_BRIGHTNESS:
        raise ValueError(f'brightness {brightness} out of range')
    for color in (red, green, blue):
        if not 0 <= color <= MAX_COLOR:
            raise ValueError(f'color value {color} out of range')
    return bytes([strand << 6 | addr, brightness, blue, green, red])


def layout(orientations: Sequence[int],
           strand_order: Sequence[int]) -> Dict[int, PhysAddr]:
    """Map LED IDs to physical addresses.

    LED IDs run through the strands in the order given by strand_order.
    An orientation of 1 runs a strand away from the Pi (bulb 0 first);
    -1 runs it toward the Pi (bulb STRAND_LEN - 1 first).
    """
    if sorted(strand_order) != list(range(NUM_STRANDS)):
        raise ValueError(f'strand_order must be a permutation of 0-{NUM_STRANDS - 1}')
    if len(orientations) != NUM_STRANDS or not set(orientations) <= {1, -1}:
        raise ValueError(f'orientations must be {NUM_STRANDS} values of 1 or -1')

    phys_addr = {}
    for strand, orientation in zip(strand_order, orientations):
        addrs = range(STRAND_LEN)
        if orientation == -1:
            addrs = reversed(addrs)
        for addr in addrs:
            phys_addr[len(phys_addr)] = (strand, addr)
    return phys_addr


class Driver:
    """Writes LED updates to /dev/xmas.

    write_led() sends immediately. write_led_buffered() queues updates
    until flush_buffer(), which sends them in a single write so the
    kernel can update both strands simultaneously.
    """

    def __init__(self, orientations: Sequence[int] = (-1, 1),
                 strand_order: Sequence[int] = (0, 1), device: str = DEVICE):
        self.phys_addr = layout(orientations, strand_order)
        self.buf = bytearray()
        self.f = open(device, 'wb', buffering=0)

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def get_physical_addr(self, led_id: int) -> PhysAddr:
        try:
            return self.phys_addr[led_id]
        except KeyError:
            raise ValueError(f'LED {led_id} out of range') from None

    def frames(self, led_id: int, brightness: int,
               red: int, green: int, blue: int) -> bytes:
        """Encode an update to led_id, or to every bulb if BROADCAST.

        Broadcasts only change brightness; bulbs ignore their color.
        """
        if led_id == BROADCAST:
            return b''.join(frame((strand, BROADCAST_ADDR), brightness, 0, 0, 0)
                            for strand in range(NUM_STRANDS))
        return frame(self.get_physical_addr(led_id), brightness, red, green, blue)

    def write_led(self, led_id: int, brightness: int,
                  red: int, green: int, blue: int):
        self._write(self.frames(led_id, brightness, red, green, blue))

    def write_led_buffered(self, led_id: int, brightness: int,
                           red: int, green: int, blue: int):
        self.buf += self.frames(led_id, brightness, red, green, blue)

    def set_all(self, brightness: int, red: int, green: int, blue: int):
        """Set every LED, sending all updates in one write."""
        for led_id in range(NUM_LEDS):
            self.write_led_buffered(led_id, brightness, red, green, blue)
        self.flush_buffer()

    def flush_buffer(self):
        self._write(self.buf)
        self.buf.clear()

    def _write(self, data: Union[bytes, bytearray]):
        view = memoryview(data)
        while view:
            view = view[self.f.write(view):]


def test_pattern(d: Driver):
    d.write_led(0, 200, 0, 0, 15)
    d.write_led(NUM_LEDS - 1, 200, 15, 0, 0)
    for led_id in range(NUM_LEDS):
        d.write_led(led_id, 200, 13, 0, 13)
        time.sleep(0.05)


def main():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [LED | --set-all] [BRIGHTNESS RED GREEN BLUE]',
        description='With no arguments, play a test pattern: '
                    f'LED 0 blue, LED {NUM_LEDS - 1} red, then a magenta chase. '
                    'Otherwise set one LED, or every LED with --set-all.',
        epilog=f'LED is 0-{NUM_LEDS - 1}, or {BROADCAST} to set only the brightness '
               f'of every bulb. BRIGHTNESS is 0-{MAX_BRIGHTNESS}; RED, GREEN, and '
               f'BLUE are 0-{MAX_COLOR}.')
    parser.add_argument('--set-all', action='store_true', help='set every LED')
    parser.add_argument('values', nargs='*', type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.set_all and len(args.values) != 4:
        parser.error('--set-all takes BRIGHTNESS RED GREEN BLUE')
    if not args.set_all and len(args.values) not in (0, 5):
        parser.error('give LED BRIGHTNESS RED GREEN BLUE, or no arguments')

    with Driver() as d:
        try:
            if args.set_all:
                d.set_all(*args.values)
            elif args.values:
                d.write_led(*args.values)
            else:
                test_pattern(d)
        except ValueError as e:
            parser.error(str(e))


if __name__ == '__main__':
    main()
