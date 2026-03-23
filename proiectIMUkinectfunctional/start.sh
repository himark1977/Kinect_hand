#!/bin/bash

PIPE="/tmp/kinect_pipe"

# Creează FIFO dacă nu există
if [[ ! -p $PIPE ]]; then
    mkfifo $PIPE
fi

# Rulează C++ Kinect în background și ia PID-ul
./kinect_hand > $PIPE &
KINECT_PID=$!

# Rulează Python care citește din pipe
python3 imu2.py

# La final, oprește C++ Kinect
kill $KINECT_PID
