#!/bin/bash
#
# Network watchdog
#
# Report IP address using the server API.
# If connectivity is lost, blink warning pattern. Reboot if it isn't restored soon.

cd "$(dirname "$0")" || exit 1

HELLO_URL="https://blinken.org/api/0/hello-pi"
MAX_FAILURES=300
CHECK_INTERVAL=900

say_hello() {
    curl -s --max-time 10 -o /dev/null "$HELLO_URL"
}

# blink SECONDS BRIGHTNESS RED GREEN BLUE: turn all bulbs off, then
# to the given color, holding each for SECONDS
blink() {
    ./driver.py --set-all 0 0 0 0
    sleep "$1"
    ./driver.py --set-all "$2" "$3" "$4" "$5"
    sleep "$1"
}

while true; do
    failures=0
    until say_hello; do
        blink .5 128 13 0 0    # red

        if (( ++failures > MAX_FAILURES )); then
            echo "Network didn't come up, rebooting"
            reboot
        fi
    done

    echo "Network is up"

    for _ in {1..5}; do
        blink .1 100 0 13 0    # green
    done

    sleep "$CHECK_INTERVAL"
    while say_hello; do
        sleep "$CHECK_INTERVAL"
    done

    echo "Network is down"
done
