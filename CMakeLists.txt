cmake_minimum_required(VERSION 3.10)
project(kinect_hand)

find_package(OpenCV REQUIRED)

include_directories(
    /usr/local/include/libfreenect
    ${OpenCV_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}/include
)

link_directories(/usr/local/lib)

add_executable(kinect_hand main.cpp serial.cpp)

target_link_libraries(kinect_hand
    freenect
    ${OpenCV_LIBS}
    pthread
)