#!/bin/bash

# Load kernel module; it creates /dev/xmas itself.
# Pass e.g. strand0_gpio=17 strand1_gpio=18 to override the pins.
insmod "$(dirname "$0")/xmas.ko" "$@"
chmod 222 /dev/xmas
