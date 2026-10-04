#!/bin/bash
#
# Start the lights: load the kernel module, play a test pattern, then
# serve UDP updates and watch the network.

cd "$(dirname "$0")" || exit 1

echo "Loading kernel module"
lkm/setup.sh || exit 1

echo "Testing strands"
./driver.py

echo "Launching UDP driver"
driver/udp-driver &

echo "Connecting to blinken.org stream"
./stream-client.py &

echo "Monitoring network status"
exec ./network.sh
