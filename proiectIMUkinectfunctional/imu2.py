import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import serial
import math
import os
import time
import fcntl  # pentru non-blocking pipe
import csv
# ---------- CONFIG ---------- #
PIPE_PATH = "/tmp/kinect_pipe"
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
TIMEOUT = 0.01  # secunde
DISPLAY_SIZE = (640, 480)
SCALE = 0.01   # scalare Kinect -> OpenGL

CSV_FILE = "imu_kinect_data.csv"

# ---------- STRUCTURI ---------- #
class IMU:
    def __init__(self):
        self.Roll = 0.0
        self.Pitch = 0.0
        self.Yaw = 0.0
        self.px = 0.0
        self.py = 0.0
        self.pz = 3.0

myimu = IMU()

# ---------- OPENGL ---------- #
def InitPygame():
    pygame.init()
    pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("IMU + Kinect Visualizer")

def InitGL():
    glClearColor(46/255,45/255,64/255,1)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, (DISPLAY_SIZE[0]/DISPLAY_SIZE[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def DrawCube():
    vertices = [
        [1,1,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],
        [1,1,1],[1,-1,1],[-1,-1,1],[-1,1,1]
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def DrawGL():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Camera follow cubul
    eye_x, eye_y, eye_z = 0, 2, -10
    center_x, center_y, center_z = myimu.px, myimu.py, myimu.pz
    up_x, up_y, up_z = 0,1,0
    gluLookAt(eye_x, eye_y, eye_z,
              center_x, center_y, center_z,
              up_x, up_y, up_z)

    glPushMatrix()
    glTranslatef(myimu.px, myimu.py, myimu.pz)
    glRotatef(myimu.Roll, 0, 0, -1)
    glRotatef(myimu.Pitch, -1, 0, 0)
    glRotatef(myimu.Yaw, 0,-1, 0)
    DrawCube()
    glPopMatrix()
    pygame.display.flip()

# ---------- CALIBRARE ---------- #
offset_x = 0.0
offset_y = 0.0
offset_z = 0.0

def CalibrateKinect(duration=2.0):
    global offset_x, offset_y, offset_z
    print("Calibrare Kinect: tine mana in pozitia centrala...")

    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)

    pipe = open(PIPE_PATH, "r")
    fd = pipe.fileno()
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    start_time = time.time()
    samples = 0
    sum_x = sum_y = sum_z = 0.0

    while time.time() - start_time < duration:
        try:
            line = pipe.readline()
            if not line:
                continue
            x, y, z = map(float, line.strip().split())
            sum_x += x
            sum_y += y
            sum_z += z
            samples += 1
        except Exception:
            continue

    if samples > 0:
        offset_x = sum_x / samples
        offset_y = sum_y / samples
        offset_z = sum_z / samples
        print(f"Offset Kinect: ({offset_x:.2f}, {offset_y:.2f}, {offset_z:.2f})")
    else:
        print("Calibrare esuata: nu s-au primit date.")

    pipe.close()

# ---------- THREAD KINECT ---------- #
def KinectThread():
    global myimu
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)

    pipe = open(PIPE_PATH, "r")
    fd = pipe.fileno()
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    while True:
        try:
            line = pipe.readline()
            if not line:
                continue
            x, y, z = map(float, line.strip().split())
            myimu.px = (x - offset_x) * SCALE
            myimu.py = (y - offset_y) * SCALE
            myimu.pz = (z - offset_z) * SCALE
        except Exception:
            continue

# ---------- THREAD IMU ---------- #
def IMUThread():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    # Calibrare gyro offset
    gx_offset = gy_offset = gz_offset = 0.0
    samples = 500
    for _ in range(samples):
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue
        try:
            numbers = [float(x) for x in line.split(',') if x.strip()]
            gx_offset += numbers[3]
            gy_offset += numbers[4]
            gz_offset += numbers[5]
        except Exception:
            continue
    gx_offset /= samples
    gy_offset /= samples
    gz_offset /= samples

    roll_gyro = pitch_gyro = yaw_gyro = 0.0

    while True:
        last_time = time.time()
        dt = time.time() - last_time
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue
        try:
            numbers = [float(x) for x in line.split(',') if x.strip()]
            if len(numbers) < 6:
                continue
            ax, ay, az = numbers[0], numbers[1], numbers[2]
            gx, gy, gz = numbers[3]-gx_offset, numbers[4]-gy_offset, numbers[5]-gz_offset

            roll_acc = math.atan2(ay, math.sqrt(ax*ax+az*az))*180/math.pi
            pitch_acc = math.atan2(-ax, math.sqrt(ay*ay+az*az))*180/math.pi

            roll_gyro  += gx*dt
            pitch_gyro += gy*dt
            yaw_gyro   += gz*dt
            
            g = 9.81  # accelerația gravitațională
            a_total = math.sqrt(ax*ax + ay*ay + az*az)
            error = abs(a_total - g)

            # mapăm eroarea la alpha
            # eroare mică -> alpha mic (mai mult accel)
            # eroare mare -> alpha mare (mai mult giro)
            alpha_min = 0.90
            alpha_max = 0.99

            # clamping
            alpha = alpha_min + (alpha_max - alpha_min) * min(error / g, 1.0)
          
            myimu.Roll  = alpha*roll_gyro + (1-alpha)*roll_acc
            roll_gyro   = myimu.Roll  

            myimu.Pitch = alpha*pitch_gyro + (1-alpha)*pitch_acc
            pitch_gyro  = myimu.Pitch
            myimu.Yaw   = yaw_gyro

            # print(myimu.Roll,myimu.Pitch,myimu.Yaw,myimu.px,myimu.py,myimu.pz)
        except:
            continue

# ---------- MAIN ---------- #
def main():
    CalibrateKinect(duration=2.0)
    threading.Thread(target=KinectThread, daemon=True).start()
    threading.Thread(target=IMUThread, daemon=True).start()

    InitPygame()
    InitGL()

    clock = pygame.time.Clock()
    running = True

    with open(CSV_FILE, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        # header
        csv_writer.writerow(["time","roll","pitch","yaw","x","y","z"])

        while running:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type==KEYDOWN and event.key==K_ESCAPE):
                    running = False
            DrawGL()

            # salvare CSV
            csv_writer.writerow([
                time.time(),
                myimu.Roll,
                myimu.Pitch,
                myimu.Yaw,
                myimu.px,
                myimu.py,
                myimu.pz
            ])

            clock.tick(60)
    pygame.quit()