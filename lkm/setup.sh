#!/bin/bash
#
# Load the kernel module, which creates /dev/xmas and numbers the bulbs.
# Arguments are passed to insmod, e.g. strand0_gpio=22 strand1_gpio=23.

set -e

if [ -d /sys/module/xmas ]; then
    echo "xmas module already loaded"
    exit 0
fi

insmod "$(dirname "$0")/xmas.ko" "$@"

# The module creates /dev/xmas writable by everyone; make sure udev
# hasn't restricted it.
chmod 222 /dev/xmas
