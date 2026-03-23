import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import serial
import math
import time
import csv

# ---------- CONFIG ---------- #
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
TIMEOUT = 0.01
DISPLAY_SIZE = (640, 480)

CSV_FILE = "imu_data.csv"

csv_file = open(CSV_FILE, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["time","roll","pitch","yaw"])

# ---------- STRUCT ---------- #
class IMU:
    Roll = 0.0
    Pitch = 0.0
    Yaw = 0.0

myimu = IMU()

# ---------- OPENGL ---------- #
def InitPygame():
    pygame.init()
    pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("IMU Visualizer")

def InitGL():
    glClearColor(46/255,45/255,64/255,1)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(0, 0, -7,
              0, 0, 0,
              0, 1, 0)

    glRotatef(myimu.Roll, 1, 0, 0)
    glRotatef(myimu.Pitch, 0, 1, 0)
    glRotatef(myimu.Yaw, 0, 0, 1)

    DrawCube()
    pygame.display.flip()

# ---------- THREAD IMU ---------- #
def IMUThread():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)

    # calibrare gyro
    gx_offset = gy_offset = gz_offset = 0.0
    samples = 300

    print("Calibrare IMU... nu misca senzorul")
    count = 0
    while count < samples:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue
        try:
            nums = [float(x) for x in line.split(',')]
            gx_offset += nums[3]
            gy_offset += nums[4]
            gz_offset += nums[5]
            count += 1
        except:
            continue

    gx_offset /= samples
    gy_offset /= samples
    gz_offset /= samples

    print("Calibrare gata")

    roll_gyro = pitch_gyro = yaw_gyro = 0.0
    dt = 0.01

    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue

        try: 
            nums = [float(x) for x in line.split(',')]
            if len(nums) < 6:
                continue

            ax, ay, az = nums[0], nums[1], nums[2]
            gx, gy, gz = nums[3]-gx_offset, nums[4]-gy_offset, nums[5]-gz_offset

            roll_acc = math.atan2(ay, math.sqrt(ax*ax+az*az))*180/math.pi
            pitch_acc = math.atan2(-ax, math.sqrt(ay*ay+az*az))*180/math.pi

            roll_gyro  += gx * dt
            pitch_gyro += gy * dt
            yaw_gyro   += gz * dt

            g = 9.81  # accelerația gravitațională
            a_total = math.sqrt(ax*ax + ay*ay + az*az)
            error = abs(a_total - g)

            # mapăm eroarea la alpha
            # eroare mică -> alpha mic (mai mult accel)
            # eroare mare -> alpha mare (mai mult giro)
            alpha_min = 0.90
            alpha_max = 0.99
            k = 0.1  # cât de repede schimbă alpha

            # clamping
            alpha = alpha_min + (alpha_max - alpha_min) * min(error / g, 1.0)
          

            myimu.Roll  = alpha*roll_gyro + (1-alpha)*roll_acc
            roll_gyro   = myimu.Roll  
            myimu.Pitch = alpha*pitch_gyro + (1-alpha)*pitch_acc
            pitch_gyro  = myimu.Pitch
            myimu.Yaw   = yaw_gyro

        except:
            continue

# ---------- MAIN ---------- #
def main():
    threading.Thread(target=IMUThread, daemon=True).start()

    InitPygame()
    InitGL()

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        DrawGL()

        csv_writer.writerow([
            time.time(),
            myimu.Roll,
            myimu.Pitch,
            myimu.Yaw
        ])

        clock.tick(60)

    pygame.quit()
    csv_file.close()

if __name__ == "__main__":
    main()
