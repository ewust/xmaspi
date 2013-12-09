#!/bin/bash

# load kernel module
cd ~pi/xmaspi/lkm
insmod xmas.ko
mknod /dev/xmas c 252 0
chmod 222 /dev/xmas

# run the init script
cd ~pi/xmaspi
./driver.py


# red status
./driver.py 99 200 0 0 13

# start wireless
./start-wireless.sh&


# blink last LED to show we are done
for i in `seq 1 5`
do
    ./driver.py 99 0 0 13 0
    ./driver.py 99 200 0 13 0
done

# show our ip address on the LEDs
./ip.py &
pid=$!
sleep 5
kill $pid


ntpdate -ub 0.us.pool.ntp.org

#su xmaslights
#cd /home/xmaslights/xmaspi/
#./xmas.py &

