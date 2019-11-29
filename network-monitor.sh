#!/bin/bash
command > /dev/null 2>&1
while true ; do
    if ifconfig wlan0 | grep -q "inet addr:" ; then
        sleep 60
    else
        ifup --force wlan0
        sleep 10
    fi
done

