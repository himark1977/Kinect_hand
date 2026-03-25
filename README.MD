# IMU and Kinect Hand Tracking Project

This project combines data from an Inertial Measurement Unit (IMU) sensor and a Kinect device to track and visualize hand movements in 3D space. It uses OpenGL for rendering a 3D cube that represents the hand's orientation and position.

## Overview

The system consists of:
- **IMU Sensor**: Provides accelerometer and gyroscope data for orientation (roll, pitch, yaw).
- **Kinect Device**: Tracks hand position in 3D space (x, y, z coordinates).
- **Visualization**: A Python application using Pygame and OpenGL to display a rotating cube based on the sensor data.

Data is collected in real-time and can be logged to CSV files for analysis.

## Prerequisites

- **Hardware**:
  - IMU sensor connected via serial (e.g., `/dev/ttyUSB0`)
  - Kinect device (for hand tracking)
- **Software**:
  - Python 3.x with libraries: `pygame`, `pyopengl`, `pyserial`, `math`, `time`, `csv`, `threading`, `os`, `fcntl`
  - C++ compiler (e.g., g++)
  - CMake for building C++ components
  - Linux environment (for serial and pipe communication)

## Installation

1. **Clone or navigate to the project directory**:
   ```
   cd /home/adria/Kinect_hand/proiectIMUkinectfunctional
   ```

2. **Build the C++ components**:
   - Ensure CMake is installed.
   - Run in the root directory (where CMakeLists.txt is):
     ```
     mkdir build
     cd build
     cmake ..
     make
     ```
   - This will generate the `kinect_hand` executable.

3. **Install Python dependencies**:
   ```
   pip install pygame pyopengl pyserial
   ```

4. **Set up permissions** (if needed):
   - Ensure access to serial port: `sudo chmod 666 /dev/ttyUSB0`
   - For pipe communication: The scripts create `/tmp/kinect_pipe` if needed.

5. **Install opencv**:
```sudo apt install libopencv-dev```

## Usage

### Running the Full System (IMU + Kinect)
- Execute the main Python script:
  ```
  python imu2_kinect.py
  ```
- This will:
  - Calibrate the Kinect (hold hand in center position).
  - Start threads for IMU and Kinect data reading.
  - Open an OpenGL window showing the cube.
  - Log data to `imu_kinect_data.csv`.

### Running IMU Only
- For testing without Kinect:
  ```
  python imu2_nokinect.py
  ```
- Logs to `imu_data.csv`.

### Running Kinect Data Producer
- The C++ executable `kinect_hand` reads Kinect data and writes to a named pipe.
- Run it in the background or separately.

### Starting Script
- Use `start.sh` to automate launching components.

## File Descriptions

- **imu2_kinect.py**: Main script integrating IMU and Kinect. Includes calibration, threading for data reading, OpenGL visualization, and CSV logging.
- **imu2_nokinect.py**: Simplified version for IMU only, without Kinect integration.
- **imu2 (Copy).py**: Backup or variant of the main script.
- **imu_opengl.py**: Possibly an earlier version or alternative OpenGL setup.
- **imuxboxv0.py**: Another variant or test script.
- **kinect_hand**: Compiled C++ executable for Kinect data processing.
- **IMU.cpp, main.cpp, serial.cpp, header.h**: C++ source files for IMU and serial communication.
- **CMakeLists.txt**: Build configuration for C++ components.
- **data.csv**: Sample or logged data from earlier runs.
- **imu_kinect_data.csv**: Logged data with timestamps, roll/pitch/yaw, and x/y/z positions.
- **start.sh**: Shell script to start the application.
- **README.MD**: This file.

## Data Format

- **IMU Data**: Accelerometer (ax, ay, az) and gyroscope (gx, gy, gz) readings.
- **Kinect Data**: Hand position (x, y, z) in millimeters.
- **CSV Output**: Time, roll, pitch, yaw, x, y, z.

## Troubleshooting

- **Serial Connection**: Ensure IMU is connected to `/dev/ttyUSB0` and baud rate is 115200.
- **Kinect Pipe**: The named pipe `/tmp/kinect_pipe` is used for inter-process communication.
- **Calibration**: Hold the hand steady during initial calibration.
- **Dependencies**: Install missing Python packages if errors occur.

## License

[Add license if applicable]
