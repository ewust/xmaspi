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


# wait for wifi...
ifconfig | grep 192.168
r=`echo $?`
while [[ $r -eq 1 ]];
do
    ./all_on.py 0 0 0 0
    sleep .5
    ./all_on.py 128 13 0 0
    sleep .5

    ifconfig | grep 192.168
    r=`echo $?`
    
done

for i in `seq 1 5`
do
    ./all_on.py 0 0 0 0
    sleep .1
    ./all_on.py 100 0 13 0
    sleep .1
done

ntpdate -ub 0.us.pool.ntp.org

#su xmaslights
#cd /home/xmaslights/xmaspi/
#./xmas.py &

