#!/bin/bash

while true ; do
    if ifconfig wlan0 | grep -q "inet addr:" ; then
        sleep 60
    else
        echo "Network connection down! Attempting reconnection."
        python /home/pi/2048-Pi-Display/error.py &
        PID=$!
        ifup --force wlan0
        sleep 10
        pkill -signal -P PID
    fi
done