#!/bin/bash

# Network watchdog
#
# Report IP address using the server API.
# If connectivity is lost, blink warning pattern. Reboot if it isn't restored soon.

hello="https://blinken.org/api/0/hello-pi"
while [ 1 ]; do

    n=0
    curl -s "$hello" > /dev/null
    r=`echo $?`
    while [[ $r -ne 0 ]]; do
        ./set_all.py 0 0 0 0
        sleep .5
        ./set_all.py 128 13 0 0
	sleep .5

        ((n=n+1))
        if [[ "$n" -gt 300 ]]; then
            logger -s "Network didn't come up, rebooting"
            reboot
        fi
        curl -s "$hello" > /dev/null
        r=`echo $?`
    done

    logger -s "Network is up"

    for i in `seq 1 5`; do
        ./set_all.py 0 0 0 0
        sleep .1
        ./set_all.py 100 0 13 0
        sleep .1
    done

    while [[ $r -eq 0 ]]; do
        sleep 900
        curl -s "$hello" > /dev/null
        r=`echo $?`
    done

    logger -s "Network is down"

done
