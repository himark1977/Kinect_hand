#!/bin/bash

PIPE="/tmp/kinect_pipe"

# Creează FIFO dacă nu există
if [[ ! -p $PIPE ]]; then
    mkfifo $PIPE
fi

# Rulează C++ Kinect în background și scrie în pipe
./kinect_hand > $PIPE &

# Rulează Python care citește din pipe
python3 imu2.py

# La final, oprește C++ (opțional)
kill %1
