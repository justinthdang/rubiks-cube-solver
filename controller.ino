#include <Servo.h>
#include <Stepper.h>
#include <Keyboard.h>

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
  if (Serial.available() > 0) {
    char command = Serial.read();
// will add comments later too lazy rn icl
    switch (command) {
      case 'S': {
        int steps = Serial.parseInt();
        myStepper.step(steps);
        break;
      }    
      case 'F': {
        int angle = Serial.parseInt();
        myServo.write(angle);
        break;
      }
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
    }
}
