## Files description
IMU.cpp build and upload on MCU.
imu_opengl.py and proiectIMUkinectfunctional/imu2.py it's the same file
imuxboxv0.py use MCU as virtual xbox controller

main.cpp, serial.cpp, header.h, CmakeLists.txt it's for kinect.

## Build 

git clone https://github.com/OpenKinect/libfreenect.git
cd libfreenect
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig

mkdir build && cd build
cmake ..
make
./kinect_hand

## Run the project
./proiectIMUkinectfunctional/start.sh
