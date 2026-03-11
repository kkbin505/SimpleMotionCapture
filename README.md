# Simple Motion Capture Project

A real-time wireless 3D motion capture and visualization system designed for immersive interaction. This project uses ESP32-S3 microcontrollers and IMU sensors (BMI160/MPU series) to track motion and render a virtual lightsaber with sound effects and motion trails.

## 🚀 Features

- **Real-time 3D Rendering**: High-performance visualization using Matplotlib and NumPy.
- **Dynamic Trail Effect**: Visualizes motion paths with fading trails.
- **Immersive Sound System**: Pygame-based sound engine with swing detection and hum volume modulation.
- **Wireless Connection**: Uses ESP-NOW for low-latency wireless data transmission between transmitter and receiver.
- **Calibration Tool**: Easy axis alignment calibration via keyboard.

## 📁 Project Structure

- `lightsaber_3d.py`: The main application featuring the 3D lightsaber, sounds, and trail effects.
- `mocap_transmitter/`: PlatformIO project for the ESP32-S3 transmitter (connected to the sensor).
- `mocap_receiver/`: PlatformIO project for the ESP32-S3 receiver (connected to the PC).
- `assets/`: Audio files (`.wav`) for the lightsaber hum, ignition, and swing.

## 🛠 Setup & Installation

### Hardware Requirements
- 2x ESP32-S3 Development Boards.
- 1x BMI160 or MPU6050 IMU Sensor.
- USB Cables for PC communication.

### Software Requirements
- Python 3.9+
- Dependencies:
  ```bash
  pip install pyserial numpy matplotlib pygame
  ```

### Firmware Upload
1. Open `mocap_transmitter` and `mocap_receiver` in VS Code with PlatformIO.
2. Build and upload the transmitter code to the board attached to the sensor.
3. Build and upload the receiver code to the board attached to your PC.

## 🎮 How to Use

1. **Check Serial Port**: Update `SERIAL_PORT` in `lightsaber_3d.py` to match your receiver's COM port (default is `COM11`).
2. **Run Visualization**:
   ```bash
   python lightsaber_3d.py
   ```
3. **Calibrate**: Hold the sensor in the "upward" position and press **'c'** to reset the orientation.
4. **Move**: Move the transmitter, and watch the lightsaber follow your movements in 3D.

## 🧹 Maintenance

- Use `.gitignore` to keep the repository clean of temporary build files (`.pio`, `__pycache__`).
- All code comments and UI elements have been translated to English for international compatibility.

## 📜 License

MIT License. Feel free to use and modify for your Jedi training!
