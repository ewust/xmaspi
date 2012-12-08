#!/bin/bash

while [ 1 ]; do

    iwconfig 2>&1 | grep xmaslights > /dev/null
    r=`echo $?`
    while [[ $r -eq 1 ]];
    do 
        iwconfig wlan1 essid xmaslights
        sleep 1
        iwconfig 2>&1 | grep xmaslights > /dev/null
        r=`echo $?`
    done

    sleep 10

done
