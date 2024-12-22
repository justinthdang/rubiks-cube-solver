#include <Servo.h>
#include <Stepper.h>
#include <Keyboard.h>

const int servoPin = 3;
const int stepsPerRevolution = 2038;

Servo myServo;
Stepper myStepper(stepsPerRev, 8, 10, 9, 11);

// initialize settings
void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);
  myStepper.setSpeed()
}


void loop() {
  // put your main code here, to run repeatedly:

}
