import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# --- Configuration ---
SERIAL_PORT = 'COM11'  # Updated to match detected receiver port
BAUD_RATE = 115200

# --- Setup Visualization ---
fig = plt.figure(figsize=(10, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('black')
ax.set_title("3D Motion Capture - ESP32-S3 + MPU9250", color='white')

# Plotting axes lines for orientation
# Red: X, Green: Y, Blue: Z
line_x, = ax.plot([0, 1], [0, 0], [0, 0], color='red', linewidth=3, label='X')
line_y, = ax.plot([0, 0], [0, 1], [0, 0], color='lime', linewidth=3, label='Y')
line_z, = ax.plot([0, 0], [0, 0], [0, 1], color='cyan', linewidth=3, label='Z')

# Customize grid and labels
ax.grid(False)
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.set_xlim([-1.2, 1.2])
ax.set_ylim([-1.2, 1.2])
ax.set_zlim([-1.2, 1.2])
ax.set_axis_off()
ax.legend(labelcolor='white', facecolor='black')

# --- Serial Reader ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Successfully connected to {SERIAL_PORT}")
except Exception as e:
    print(f"Could not open serial port {SERIAL_PORT}: {e}")
    ser = None

def get_sensor_data():
    if ser and ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # Handle debug prefix if present
            if line.startswith("RECV <- "):
                line = line.replace("RECV <- ", "")
            
            # Expected format: ax,ay,az,gx,gy,gz,mx,my,mz,timestamp
            parts = line.split(',')
            if len(parts) >= 9:
                return [float(p) for p in parts[:9]]
        except Exception as e:
            # print(f"Parse error: {e}")
            pass
    return None

# Initial Orientation
roll, pitch, yaw = 0, 0, 0

def update_plot(frame):
    global roll, pitch, yaw
    
    data = get_sensor_data()
    if data:
        ax_val, ay_val, az_val, gx, gy, gz, mx, my, mz = data
        
        # 1. Simple Pitch and Roll from Accelerometer (Basic Tilt)
        # Roll: rotation around X axis
        roll = np.arctan2(ay_val, az_val)
        # Pitch: rotation around Y axis
        pitch = np.arctan2(-ax_val, np.sqrt(ay_val**2 + az_val**2))
        
        # 2. Simple Yaw (Compass)
        # This requires tilt compensation for accuracy, but here's a basic version:
        # Note: MPU9250 magnetometer X/Y/Z may need re-alignment with Accel/Gyro
        mag_x_comp = mx * np.cos(pitch) + mz * np.sin(pitch)
        mag_y_comp = mx * np.sin(roll) * np.sin(pitch) + my * np.cos(roll) - mz * np.sin(roll) * np.cos(pitch)
        yaw = np.arctan2(-mag_y_comp, mag_x_comp)

    # Rotation Matrices
    R_x = np.array([[1, 0, 0], 
                    [0, np.cos(roll), -np.sin(roll)], 
                    [0, np.sin(roll), np.cos(roll)]])
    
    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)], 
                    [0, 1, 0], 
                    [-np.sin(pitch), 0, np.cos(pitch)]])
    
    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0], 
                    [np.sin(yaw), np.cos(yaw), 0], 
                    [0, 0, 1]])
    
    # Combined Rotation (Intrinsic XYZ sequence)
    R = R_z @ R_y @ R_x
    
    # Transform base axes
    # X axis vector
    vec_x = R @ np.array([1, 0, 0])
    # Y axis vector 
    vec_y = R @ np.array([0, 1, 0])
    # Z axis vector
    vec_z = R @ np.array([0, 0, 1])
    
    # Update Plot Lines
    line_x.set_data_3d([0, vec_x[0]], [0, vec_x[1]], [0, vec_x[2]])
    line_y.set_data_3d([0, vec_y[0]], [0, vec_y[1]], [0, vec_y[2]])
    line_z.set_data_3d([0, vec_z[0]], [0, vec_z[1]], [0, vec_z[2]])
    
    return line_x, line_y, line_z

# Run Animation
ani = FuncAnimation(fig, update_plot, interval=20, blit=True, cache_frame_data=False)
plt.show()

if ser:
    ser.close()
