#!/usr/bin/env python3
"""Set every LED to the same brightness and color."""

import argparse

from driver import MAX_BRIGHTNESS, MAX_COLOR, NUM_LEDS, Driver


def set_all(d: Driver, brightness: int, red: int, green: int, blue: int):
    for led_id in range(NUM_LEDS):
        d.write_led_buffered(led_id, brightness, red, green, blue)
    d.flush_buffer()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('brightness', type=int, help=f'0-{MAX_BRIGHTNESS}')
    parser.add_argument('red', type=int, help=f'0-{MAX_COLOR}')
    parser.add_argument('green', type=int, help=f'0-{MAX_COLOR}')
    parser.add_argument('blue', type=int, help=f'0-{MAX_COLOR}')
    args = parser.parse_args()

    with Driver() as d:
        try:
            set_all(d, args.brightness, args.red, args.green, args.blue)
        except ValueError as e:
            parser.error(str(e))


if __name__ == '__main__':
    main()
