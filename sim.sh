#!/bin/bash

count=$1
pass=$2

if [ -z $count ]; then
    echo "missing simulated user count";
    exit 1;
fi

if [ -z $pass ]; then
    echo "missing user zenoss password";
    exit 1;
fi

logdir="$(pwd)/log"
user="zenny"
workflows="MonitorEvents, InvestigateDevice, MonitorDashboard, InvestigateDevice, MonitorDevices"
simId="dockerSim$RANDOM"
duration=900

docker run --privileged \
    -v "$logdir":/root/log \
    -v /dev/shm:/dev/shm \
    -v /etc/hosts:/etc/hosts \
    zenoss/usersim:v2 \
    -u https://zenoss5.graveyard.zenoss.loc \
    -n $user \
    -p $pass \
    -c $count \
    --duration $duration \
    --log-dir ./log \
    --tsdb-url https://opentsdb.graveyard \
    --workflows "$workflows" \
    --simId "$simId"
