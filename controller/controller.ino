// import libraries
#include <Servo.h>
#include <Stepper.h>
#include <Keyboard.h>

// initialize variables and objects for servo and stepper motors
const int servoPin = 3;
const int stepsPerRev = 2048;
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
      // 'A' controls the stepper
      case 'A': {
        int steps = Serial.parseInt();
        myStepper.step(steps);
        break;
      }
      // 'B' controls the servo
      case 'B': {
        int angle = Serial.parseInt();
        myServo.write(angle);
        break;
      }
      // 'C' simulates the keypress "f"
      case 'C': {
        delay(1000);
        Keyboard.press("f");
        delay(1000);
        Keyboard.releaseAll();
        break;
      }
      default: {
        break;
      }
      // 'D' simulates the keypress "q"
      case 'D': {
        delay(1000);
        Keyboard.press("q");
        delay(1000);
        Keyboard.releaseAll();
        break;
      }
      default: {
        break;
      }
    }
}
