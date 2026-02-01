
int ReadSerial();
int Calibration();
int ReadData();

class IMU {
    public:
        float Roll=0.0f;
        float Pitch=0.0f;
        float Yaw=0.0f;
        float gx_offset=0.0f;
        float gy_offset=0.0f;
        float gz_offset=0.0f;
        float alpha = 0.96;
        float numbers[6];
};