#!/bin/bash

count=$1
pass=$2
simId=${3:-"dockerSim$RANDOM"}

if [ -z $count ]; then
    echo "missing simulated user count";
    exit 1;
fi

if [ -z $pass ]; then
    echo "missing user zenoss password";
    exit 1;
fi

logdir="$(pwd)/log"
user="testuser1"
workflows="MonitorEvents, InvestigateDevice, MonitorDashboard, InvestigateDevice, MonitorDevices"
duration=900

docker run --privileged \
    -v "$logdir":/root/log \
    -v /dev/shm:/dev/shm \
    -v /etc/hosts:/etc/hosts \
    zenoss/usersim:v3 \
    -u https://zenoss5.zenoss.com \
    -n $user \
    -p $pass \
    -c $count \
    --duration $duration \
    --log-dir ./log \
    --tsdb-url http://10.88.122.63:32791 \
    --workflows "$workflows" \
    --simId "$simId"
