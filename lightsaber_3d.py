import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import pygame
import os

# --- Configuration ---
SERIAL_PORT = 'COM11'  # Read from receiver (ESP-NOW)
BAUD_RATE = 115200


# --- Sound Setup ---
pygame.mixer.init()
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    on_sound = pygame.mixer.Sound(os.path.join(script_dir, 'lightsaber_on.wav'))
    hum_sound = pygame.mixer.Sound(os.path.join(script_dir, 'lightsaber_hum.wav'))
    swing_sound = pygame.mixer.Sound(os.path.join(script_dir, 'lightsaber_swing.wav'))
    
    # on_sound.play() # Play activation sound (Commented out for quiet startup)
    # time.sleep(0.5)
    hum_channel = hum_sound.play(-1) # Loop hum indefinitely
    hum_channel.set_volume(0.3)
    # print("Force Sounds Initialized - Files loaded from Lightsaber repo")
except Exception as e:
    print(f"Sound initialization failed: {e}")
    hum_channel = None

# --- Setup Visualization ---
fig = plt.figure(figsize=(10, 10), facecolor='black')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('black')
ax.set_title("Jedi Master Mocap - Trail Effect Enabled", color='white', pad=20)

# Lightsaber Components
handle_line, = ax.plot([0, 0], [0, 0], [0, 0.3], color='#888888', linewidth=8, solid_capstyle='round')
blade_line, = ax.plot([0, 0], [0, 0], [0.3, 1.3], color='#00FFFF', linewidth=5, solid_capstyle='round')
glow_line, = ax.plot([0, 0], [0, 0], [0.3, 1.3], color='#00FFFF', linewidth=15, alpha=0.3, solid_capstyle='round')

# Trail Components
TRAIL_LENGTH = 10
trail_lines = [ax.plot([0, 0], [0, 0], [0.3, 1.3], color='#00FFFF', linewidth=2, alpha=0.1)[0] for _ in range(TRAIL_LENGTH)]
trail_history = [] # Stores [p1_r, p2_r] pairs

# Customize grid and labels
ax.grid(False)
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])
ax.set_axis_off()

# --- Serial Utils ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Force-Link Established to {SERIAL_PORT}")
except Exception as e:
    print(f"Could not open serial port {SERIAL_PORT}: {e}")
    ser = None

def get_sensor_data():
    latest_data = None
    if ser and ser.in_waiting:
        try:
            # Continuously flush the buffer to get the freshest data and avoid blocking
            while ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith("RECV <- "): line = line.replace("RECV <- ", "")
                parts = line.split(',')
                if len(parts) >= 7: 
                    latest_data = [float(p) for p in parts[:7]]
        except: 
            pass
    return latest_data

# State
last_gyro_mag = 0
SWING_THRESHOLD = 80.0 # Adjust based on sensitivity (degrees/sec)
last_time = time.time()
R_current = np.eye(3)
R_offset = np.eye(3)

def update_plot(frame):
    global R_current, R_offset, trail_history, last_gyro_mag, last_time
    
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    global R_current
    data = get_sensor_data()
    if data:
        q0, q1, q2, q3, gx, gy, gz = data
        
        # Convert Quaternion to Base Rotation Matrix
        R_base = np.array([
            [1 - 2*(q2**2 + q3**2), 2*(q1*q2 - q0*q3), 2*(q1*q3 + q0*q2)],
            [2*(q1*q2 + q0*q3), 1 - 2*(q1**2 + q3**2), 2*(q2*q3 - q0*q1)],
            [2*(q1*q3 - q0*q2), 2*(q2*q3 + q0*q1), 1 - 2*(q1**2 + q2**2)]
        ])
        
        # Hardware Axis Alignment Correction:
        # 1. Yaw and Roll swapped means exchanging X and Z axes (or applying a 90-degree relative rotation)
        # 2. Pitch is inverted means negating the Y axis influence or applying an inversion matrix
        
        # Simplified axis alignment: use raw sensor attitude and rely on 'c' key for calibration mapping
        T_align = np.eye(3)
        
        # Apply transformation to the base rotation
        R_current = T_align @ R_base
        
        # Sound Logic: Detect Swing intensity from Gyroscope
        gyro_mag = np.sqrt(gx**2 + gy**2 + gz**2)
        if gyro_mag > SWING_THRESHOLD and last_gyro_mag <= SWING_THRESHOLD:
            try: swing_sound.play()
            except: pass
        
        # Dynamic Hum Volume based on movement
        if hum_channel:
            vol = 0.3 + min(0.7, gyro_mag * 0.1)
            hum_channel.set_volume(vol)
        
        last_gyro_mag = gyro_mag

    # Apply calibration offset so 'c' key centers the sword
    R = R_offset @ R_current
    
    # Points
    p0_r = R @ np.array([0, 0, 0])
    p1_r = R @ np.array([0, 0, 0.3])
    p2_r = R @ np.array([0, 0, 1.3])
    
    # Update Trail
    trail_history.insert(0, (p1_r.copy(), p2_r.copy()))
    if len(trail_history) > TRAIL_LENGTH:
        trail_history.pop()
    
    # Render Trail
    for i, t_line in enumerate(trail_lines):
        if i < len(trail_history):
            tp1, tp2 = trail_history[i]
            t_line.set_data_3d([tp1[0], tp2[0]], [tp1[1], tp2[1]], [tp1[2], tp2[2]])
            # Fade out
            t_line.set_alpha(max(0, 0.2 - i * 0.02))
            t_line.set_linewidth(max(0.5, 3 - i * 0.3))
        else:
            t_line.set_data_3d([], [], [])

    # Main Saber
    handle_line.set_data_3d([p0_r[0], p1_r[0]], [p0_r[1], p1_r[1]], [p0_r[2], p1_r[2]])
    blade_line.set_data_3d([p1_r[0], p2_r[0]], [p1_r[1], p2_r[1]], [p1_r[2], p2_r[2]])
    glow_line.set_data_3d([p1_r[0], p2_r[0]], [p1_r[1], p2_r[1]], [p1_r[2], p2_r[2]])
    
    return [handle_line, blade_line, glow_line] + trail_lines

def on_key(event):
    global R_offset, R_current
    if event.key.lower() == 'c':
        # Calibration goal: When 'c' is pressed, force lightsaber to point vertically up (World Z-axis)
        R_initial = np.eye(3)
        # Compute offset: first undo current orientation, then apply initial alignment
        R_offset = R_initial @ np.linalg.inv(R_current)
        print("Calibration complete! Current orientation set to vertically up.")

fig.canvas.mpl_connect('key_press_event', on_key)

ani = FuncAnimation(fig, update_plot, interval=20, blit=True, cache_frame_data=False)
plt.show()

if ser:
    ser.close()
