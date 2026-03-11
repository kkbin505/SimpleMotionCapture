import serial
import time

try:
    ser = serial.Serial('COM12', 115200, timeout=1)
    # Force a reset on some ESP32 boards
    ser.setDTR(False)
    time.sleep(0.5)
    ser.setDTR(True)
    
    print("Reading serial from COM12 for 10 seconds...")
    start_time = time.time()
    while time.time() - start_time < 10:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
    ser.close()
except Exception as e:
    print(f"Error: {e}")
