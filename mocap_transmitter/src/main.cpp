#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include <esp_now.h>

const int BMI160_ADDR = 0x69;
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

typedef struct struct_message {
  float q0, q1, q2, q3;
  float gx, gy, gz;
  uint32_t timestamp;
} struct_message;

struct_message sensorData;
esp_now_peer_info_t peerInfo;

float q0 = 1.0f, q1 = 0.0f, q2 = 0.0f, q3 = 0.0f;
float twoKp = 2.0f;
float twoKi = 0.0f;
float integralFBx = 0.0f, integralFBy = 0.0f, integralFBz = 0.0f;
uint32_t lastUpdate = 0;

void writeRegister(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

void initBMI160() {
  Wire.begin(8, 9);
  writeRegister(0x7E, 0xB6); // Soft reset
  delay(100);
  writeRegister(0x7E, 0x11); // Accel normal
  delay(50);
  writeRegister(0x7E, 0x15); // Gyro normal
  delay(100);
  writeRegister(0x41, 0x05); // +-4g
  writeRegister(0x40, 0x28); // 100Hz ODR
  writeRegister(0x43, 0x01); // 1000 dps
  writeRegister(0x42, 0x28); // 100Hz ODR
}

void MahonyAHRSupdateIMU(float gx, float gy, float gz, float ax, float ay,
                         float az, float dt) {
  float recipNorm;
  float halfvx, halfvy, halfvz;
  float halfex, halfey, halfez;
  float qa, qb, qc;

  if (!((ax == 0.0f) && (ay == 0.0f) && (az == 0.0f))) {
    recipNorm = 1.0f / sqrt(ax * ax + ay * ay + az * az);
    ax *= recipNorm;
    ay *= recipNorm;
    az *= recipNorm;

    halfvx = q1 * q3 - q0 * q2;
    halfvy = q0 * q1 + q2 * q3;
    halfvz = q0 * q0 - 0.5f + q3 * q3;

    halfex = (ay * halfvz - az * halfvy);
    halfey = (az * halfvx - ax * halfvz);
    halfez = (ax * halfvy - ay * halfvx);

    if (twoKi > 0.0f) {
      integralFBx += twoKi * halfex * dt;
      integralFBy += twoKi * halfey * dt;
      integralFBz += twoKi * halfez * dt;
      gx += integralFBx;
      gy += integralFBy;
      gz += integralFBz;
    } else {
      integralFBx = 0.0f;
      integralFBy = 0.0f;
      integralFBz = 0.0f;
    }

    gx += twoKp * halfex;
    gy += twoKp * halfey;
    gz += twoKp * halfez;
  }

  gx *= (0.5f * dt);
  gy *= (0.5f * dt);
  gz *= (0.5f * dt);
  qa = q0;
  qb = q1;
  qc = q2;
  q0 += (-qb * gx - qc * gy - q3 * gz);
  q1 += (qa * gx + qc * gz - q3 * gy);
  q2 += (qa * gy - qb * gz + q3 * gx);
  q3 += (qa * gz + qb * gy - qc * gx);

  recipNorm = 1.0f / sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
  q0 *= recipNorm;
  q1 *= recipNorm;
  q2 *= recipNorm;
  q3 *= recipNorm;
}

void setup() {
  Serial.begin(115200);
  delay(100);

  WiFi.mode(WIFI_STA);
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK)
    return;

  initBMI160();
  lastUpdate = micros();
}

void loop() {
  uint32_t now = micros();
  float dt = (now - lastUpdate) / 1000000.0f;
  lastUpdate = now;

  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(0x0C);
  Wire.endTransmission(false);
  Wire.requestFrom((uint16_t)BMI160_ADDR, (uint8_t)12, (uint8_t) true);

  if (Wire.available() >= 12) {
    uint8_t buf[12];
    for (int i = 0; i < 12; i++)
      buf[i] = Wire.read();

    int16_t gx_raw = (int16_t)(buf[0] | (buf[1] << 8));
    int16_t gy_raw = (int16_t)(buf[2] | (buf[3] << 8));
    int16_t gz_raw = (int16_t)(buf[4] | (buf[5] << 8));
    int16_t ax_raw = (int16_t)(buf[6] | (buf[7] << 8));
    int16_t ay_raw = (int16_t)(buf[8] | (buf[9] << 8));
    int16_t az_raw = (int16_t)(buf[10] | (buf[11] << 8));

    float gx = gx_raw / 32.8f;
    float gy = gy_raw / 32.8f;
    float gz = gz_raw / 32.8f;

    float gx_rad = gx * 0.0174533f;
    float gy_rad = gy * 0.0174533f;
    float gz_rad = gz * 0.0174533f;

    float ax = ax_raw / 8192.0f;
    float ay = ay_raw / 8192.0f;
    float az = az_raw / 8192.0f;

    MahonyAHRSupdateIMU(gx_rad, gy_rad, gz_rad, ax, ay, az, dt);

    sensorData.q0 = q0;
    sensorData.q1 = q1;
    sensorData.q2 = q2;
    sensorData.q3 = q3;
    sensorData.gx = gx;
    sensorData.gy = gy;
    sensorData.gz = gz;
    sensorData.timestamp = millis();

    esp_now_send(broadcastAddress, (uint8_t *)&sensorData, sizeof(sensorData));
  }
  delay(10);
}
