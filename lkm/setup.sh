#!/bin/bash

# load kernel module and create character device
insmod xmas.ko
major=`awk "\\$2==\"xmas\" {print \\$1}" /proc/devices`
mknod /dev/xmas c $major 0
chmod 222 /dev/xmas
