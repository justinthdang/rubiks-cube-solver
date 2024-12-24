# import libraries
#include <Servo.h>
#include <Stepper.h>
#include <Keyboard.h>

// initialize variables and objects for servo and stepper motors
const int servoPin = 3;
const int stepsPerRev = 2038;
Servo myServo;
Stepper myStepper(stepsPerRev, 8, 10, 9, 11);

// initialize settings
void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);
  myStepper.setSpeed(50);
  Keyboard.begin();
}

void loop() {
// read character from serial port if available
  if (Serial.available() > 0) {
    char command = Serial.read();
    switch (command) {
// 'S' controls the stepper
      case 'S': {
        int steps = Serial.parseInt();
        myStepper.step(steps);
        break;
      }
// 'F' controls the servo
      case 'F': {
        int angle = Serial.parseInt();
        myServo.write(angle);
        break;
      }
// 'K' controls simulates the keypress
      case 'K': {
        delay(1000);
        Keyboard.press("f");
        delay(1000);
        Keyboard.releaseAll();
        break;
      }
      default: {
        break;
      }
    }
}
