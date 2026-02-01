import vgamepad as vg
import tkinter as tk
import time
import serial
import math

class PortSettings:
    Name = "/dev/ttyUSB1"
    Speed = 115200
    Timeout = 2
class IMU:
    Roll = 0
    Pitch = 0
    Yaw = 0
    gx_offset = 0.0
    gy_offset = 0.0
    gz_offset = 0.0
    alpha = 0.96
    roll_gyro =0
    pitch_gyro =0


myport = PortSettings()
myimu  = IMU()


def SerialConnection ():
    global serial_object
    serial_object = serial.Serial( myport.Name, baudrate= myport.Speed, timeout = myport.Timeout)

def Calibration():
    print("Starting calibration!")
    samples = 500  # câte citiri pentru calibrare
    for i in range(samples):
        serial_input = serial_object.readline().decode('utf-8').strip()
        if not serial_input:
            continue
        numbers = [float(x) for x in serial_input.split(',') if x.strip()]
        myimu.gx_offset += numbers[3]
        myimu.gy_offset += numbers[4]
        myimu.gz_offset += numbers[5]
    myimu.gx_offset /= samples
    myimu.gy_offset /= samples
    myimu.gz_offset /= samples
    print("Calibration finished!")
    print(myimu.gx_offset,myimu.gy_offset,myimu.gz_offset)


def ReadData():
    dt = 0.01

    try:
        serial_input = serial_object.readline()
        clean_string = serial_input.decode('utf-8').strip()


        # Split by comma and convert to float
        numbers = [float(x) for x in clean_string.split(',') if x.strip()]

        ax, ay, az = numbers[0], numbers[1], numbers[2]
        gx, gy, gz = numbers[3], numbers[4], numbers[5]
        gx -= myimu.gx_offset
        gy -= myimu.gy_offset
        gz -= myimu.gz_offset

        # --- Accelerometer angles ---
        roll_acc = math.atan2(ay, math.sqrt(ax*ax + az*az)) * 180 / math.pi
        pitch_acc = math.atan2(-ax, math.sqrt(ay*ay + az*az)) * 180 / math.pi

        mag = math.sqrt(ax**2 + ay**2 + az**2)

        # normalizează în G
        mag_G = mag / 9.81
        deviation = abs(1.0 - mag_G)

        if deviation < 0.05:   # foarte strict, pe masă cub aproape fix
            myimu.alpha = 0.90
        elif deviation < 0.2:  # mișcare ușoară
            myimu.alpha = 0.94
        else:                  # mișcare rapidă
            myimu.alpha = 0.97

        # --- Complementary filter ---
        myimu.Roll  = myimu.alpha * (myimu.Roll  + gx * dt) + (1.0 - myimu.alpha) * roll_acc
        myimu.Pitch = myimu.alpha * (myimu.Pitch + gy * dt) + (1.0 - myimu.alpha) * pitch_acc
        myimu.Yaw   += gz * dt  # optionally wrap to [-180,180] if needed


    except Exception as e:
        print("Serial read error:", e)

    except Exception as e:
        print("Serial read error:", e)

def bridge_loop():

    ReadData()
   # --- MAPARE SPRE STICK-URI (PLACEHOLDERS REALIZAȚI) ---
    # Mapăm Roll și Pitch (care sunt de obicei între -90 și 90) la intervalul -1.0 , 1.0
    # placeholder_lx = max(min(myimu.Pitch / 90.0, 1.0), -1.0)
    # placeholder_ly = max(min(myimu.Roll / 90.0, 1.0), -1.0)
    placeholder_lx = (myimu.Pitch / 100)
    placeholder_ly = (myimu.Roll / 100)
    
    # Pentru stick dreapta putem folosi px/py sau lăsăm 0
    placeholder_rx = -max(min(myimu.Yaw / 90.0, 1.0), -1.0)
    placeholder_ry = 0.0

    # Trimitere la controllerul virtual
    v_gamepad.left_joystick_float(x_value_float=placeholder_lx, y_value_float=placeholder_ly)
    v_gamepad.right_joystick_float(x_value_float=placeholder_rx, y_value_float=placeholder_ry)
    v_gamepad.update()

    # Actualizare UI
    visual.update_ui(placeholder_lx, placeholder_ly, placeholder_rx, placeholder_ry)

    # Rulăm bucla la fiecare 10ms (100Hz)
    root.after(10, bridge_loop)

# Inițializăm controllerul virtual
# Pe Linux, acest lucru necesită permisiuni pentru /dev/uinput
v_gamepad = vg.VX360Gamepad()

root = tk.Tk()
root.title("Emulator Controller Xbox (vgamepad)")
canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack()

class ControllerVisual:
    def __init__(self, center):
        self.cx, self.cy = center
        
        # --- Text central pentru Alpha ---
        # Folosim myimu.alpha (presupunând că obiectul myimu este accesibil global)
        self.alpha_text = canvas.create_text(self.cx, self.cy - 80, text=f"Alpha: {myimu.alpha}", font=("Arial", 12, "bold"))

        # --- Joystick Stânga ---
        self.l_pos = (self.cx - 100, self.cy)
        canvas.create_oval(self.l_pos[0]-25, self.l_pos[1]-25, self.l_pos[0]+25, self.l_pos[1]+25)
        self.l_stick = canvas.create_oval(self.l_pos[0]-10, self.l_pos[1]-10, self.l_pos[0]+10, self.l_pos[1]+10, fill="blue")
        # Text pentru valorile din stânga
        self.l_label = canvas.create_text(self.l_pos[0], self.l_pos[1] - 40, text="L: 0, 0")
        
        # --- Joystick Dreapta ---
        self.r_pos = (self.cx + 100, self.cy)
        canvas.create_oval(self.r_pos[0]-25, self.r_pos[1]-25, self.r_pos[0]+25, self.r_pos[1]+25)
        self.r_stick = canvas.create_oval(self.r_pos[0]-10, self.r_pos[1]-10, self.r_pos[0]+10, self.r_pos[1]+10, fill="red")
        # Text pentru valorile din dreapta
        self.r_label = canvas.create_text(self.r_pos[0], self.r_pos[1] - 40, text="R: 0, 0")

    def update_ui(self, lx, ly, rx, ry):
        # Update poziție joystick-uri
        canvas.coords(self.l_stick, self.l_pos[0]+(lx*20)-10, self.l_pos[1]-(ly*20)-10, 
                                    self.l_pos[0]+(lx*20)+10, self.l_pos[1]-(ly*20)+10)
        canvas.coords(self.r_stick, self.r_pos[0]+(rx*20)-10, self.r_pos[1]-(ry*20)-10, 
                                    self.r_pos[0]+(rx*20)+10, self.r_pos[1]-(ry*20)+10)
        
        # Update text valori butoane/joystick
        canvas.itemconfig(self.l_label, text=f"L: {lx:.2f}, {ly:.2f}")
        canvas.itemconfig(self.r_label, text=f"R: {rx:.2f}, {ry:.2f}")
        
        # Update text Alpha (asigură-te că myimu e actualizat)
        canvas.itemconfig(self.alpha_text, text=f"Alpha: {myimu.alpha}")

visual = ControllerVisual((300, 200))
# Pornire
SerialConnection ()
Calibration()
bridge_loop()
root.mainloop()