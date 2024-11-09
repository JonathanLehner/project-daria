#include <Arduino.h>
#include <Arduino_LSM9DS1.h>

float x, y, z;
float x_gyro, y_gyro, z_gyro;

int dt = 100;
int delay_time = 0;
int timestamp;
void setup() {
  Serial.begin(115200);
  IMU.begin();

  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  timestamp = millis();
  IMU.readAcceleration(x, y, z);
  IMU.readGyroscope(x_gyro, y_gyro, z_gyro);

  Serial.print(timestamp);
  Serial.print(", ");
  Serial.print(x);
  Serial.print(", ");
  Serial.print(y);
  Serial.print(", ");
  Serial.print(z);
  Serial.print(", ");
  Serial.print(x_gyro);
  Serial.print(", ");
  Serial.print(y_gyro);
  Serial.print(", ");
  Serial.println(z_gyro);

  delay_time = dt - (millis() - timestamp);
  if (delay_time > 0) {
    delay(delay_time);
  }
}
