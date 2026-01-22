#include <Servo.h>

Servo steering;

void setup() {
  Serial.begin(9600);
  steering.attach(9);
  steering.write(90);
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.startsWith("ANGLE:")) {
      float angle = msg.substring(6).toFloat();

      int servoAngle = map(angle, -45, 45, 45, 135);
      servoAngle = constrain(servoAngle, 45, 135);

      steering.write(servoAngle);
    }
  }
}
