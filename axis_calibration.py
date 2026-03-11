import serial
import time
import math
import sys

# --- Configuration ---
SERIAL_PORT = 'COM12'
BAUD_RATE = 115200

print(f"Connecting to {SERIAL_PORT}...")
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print("Connection established!")
except Exception as e:
    print(f"Failed to connect: {e}")
    sys.exit(1)

def get_data():
    latest_data = None
    if ser.in_waiting:
        try:
            while ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith("RECV <- "): line = line.replace("RECV <- ", "")
                parts = line.split(',')
                if len(parts) >= 9: 
                    latest_data = [float(p) for p in parts[:6]] # Only need Acc & Gyro
        except: 
            pass
    return latest_data

print("\n" + "="*60)
print("              🛠 Sensor Axis Testing Tool 🛠")
print("="*60)
print("Usage:")
print("1. [Gravity Test] Point a direction downward and check which axis A-value is ~1.0.")
print("2. [Rotation Test] Rotate the board and check which axis G-value changes most.")
print("-" * 60)
print("Press [Ctrl+C] to exit...")
print("\nFetching data...")

time.sleep(1)

try:
    while True:
        data = get_data()
        if data:
            ax, ay, az, gx, gy, gz = data
            
            # Determine which axis is pointing down (maximum gravity)
            max_acc = max(abs(ax), abs(ay), abs(az))
            down_axis = "Unknown"
            if max_acc == abs(ax): down_axis = "X" + ("+" if ax > 0 else "-")
            elif max_acc == abs(ay): down_axis = "Y" + ("+" if ay > 0 else "-")
            elif max_acc == abs(az): down_axis = "Z" + ("+" if az > 0 else "-")
            
            # Use \r to overwrite line without newline for real-time refresh
            output = f"\r[Accel g]  AX: {ax:5.2f}  AY: {ay:5.2f}  AZ: {az:5.2f}  |  "
            output += f"[Gyro °/s]  GX: {gx:6.1f}  GY: {gy:6.1f}  GZ: {gz:6.1f}  "
            output += f"|  => Pointing Down: {down_axis} Axis    "
            
            sys.stdout.write(output)
            sys.stdout.flush()
            
        time.sleep(0.05)
        
except KeyboardInterrupt:
    print("\n\nTest Finished!")
finally:
    ser.close()
