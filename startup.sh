#!/bin/bash

echo Loading kernel module

( cd lkm ; ./setup.sh )

echo Initializing strand

./driver.py

echo Launching UDP driver

./driver/udp-driver &

echo Monitoring network status

./network.sh
