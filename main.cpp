#include <libfreenect.h>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <mutex>
#include "header.h"
#include <string>

IMU myimu;

std::mutex mtx;
cv::Mat depthMat(480, 640, CV_16UC1);
cv::Mat depth8(480, 640, CV_8UC1);

void depth_cb(freenect_device*, void* depth, uint32_t) {
    std::lock_guard<std::mutex> lock(mtx);
    uint16_t* d = static_cast<uint16_t*>(depth);
    memcpy(depthMat.data, d, 640 * 480 * sizeof(uint16_t));
}

int main() {
    
    freenect_context* ctx;
    freenect_device* dev;

    if (freenect_init(&ctx, NULL) < 0) {
        std::cerr << "freenect_init failed\n";
        return 1;
    }

    freenect_set_log_level(ctx, FREENECT_LOG_WARNING);
    freenect_select_subdevices(ctx, FREENECT_DEVICE_CAMERA);

    if (freenect_open_device(ctx, &dev, 0) < 0) {
        std::cerr << "Could not open Kinect\n";
        return 1;
    }

    freenect_set_depth_callback(dev, depth_cb);
    freenect_frame_mode mode =
    freenect_find_depth_mode(FREENECT_RESOLUTION_MEDIUM, FREENECT_DEPTH_MM);

    if (!mode.is_valid) {
        std::cerr << "Invalid depth mode\n";
        return 1;
    }

    freenect_set_depth_mode(dev, mode);
    freenect_start_depth(dev);

    cv::namedWindow("Depth", cv::WINDOW_AUTOSIZE);

    while (true) {
        freenect_process_events(ctx);

        mtx.lock();
        depthMat.convertTo(depth8, CV_8U, 255.0 / 4000.0);
        mtx.unlock();

        // threshold (mana ~ 50-80 cm)
        cv::Mat mask;
        cv::inRange(depthMat, 500, 800, mask);

        // noise cleanup
        cv::erode(mask, mask, {}, {-1,-1}, 1);
        cv::dilate(mask, mask, {}, {-1,-1}, 2);

        // centroid
        cv::Moments m = cv::moments(mask, true);
        if (m.m00 > 10000) {
            int cx = int(m.m10 / m.m00);
            int cy = int(m.m01 / m.m00);

            cv::circle(depth8, {cx, cy}, 8, 255, -1);
            uint16_t z = depthMat.at<uint16_t>(cy, cx);
          std::cout << cx << " " << cy << " " << z << std::endl;
            //std::cout << myimu.numbers;
        }

        cv::imshow("Depth", depth8);
        if (cv::waitKey(1) == 27) break;
    }

    freenect_stop_depth(dev);
    freenect_close_device(dev);
    freenect_shutdown(ctx);
}

int Calibration(){
    std::cout<<"Starting Calibration" << std::endl;
    int samples = 500;
    for (int i=0;i<=samples;i++) {
        int data = ReadSerial();
    //    myimu.numbers[i] = data;
    }
    return 0;
}
