#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>

typedef struct struct_message {
  float q0, q1, q2, q3;
  float gx, gy, gz;
  uint32_t timestamp;
} struct_message;

struct_message sensorData;
volatile bool newData = false;

void OnDataRecv(const uint8_t *mac, const uint8_t *incomingData, int len) {
  if (len == sizeof(sensorData)) {
    memcpy((void *)&sensorData, incomingData, sizeof(sensorData));
    newData = true;
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  if (esp_now_init() != ESP_OK)
    return;
  esp_now_register_recv_cb(OnDataRecv);
}

void loop() {
  if (newData) {
    newData = false;
    Serial.print("RECV <- ");
    Serial.print(sensorData.q0, 4);
    Serial.print(",");
    Serial.print(sensorData.q1, 4);
    Serial.print(",");
    Serial.print(sensorData.q2, 4);
    Serial.print(",");
    Serial.print(sensorData.q3, 4);
    Serial.print(",");
    Serial.print(sensorData.gx, 2);
    Serial.print(",");
    Serial.print(sensorData.gy, 2);
    Serial.print(",");
    Serial.print(sensorData.gz, 2);
    Serial.print(",");
    Serial.println(sensorData.timestamp);
  }
  delay(2);
}
