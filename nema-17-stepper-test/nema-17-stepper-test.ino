#include <AccelStepper.h>

// Pin assignments
const int stepPin = 2;     // Connects to STEP on the driver
const int dirPin = 3;      // Connects to DIR on the driver
const int enablePin = 5;   // Optional: Connects to ENABLE on the driver
const int homeSwitchPin = 7;
int steps_command = 1000;
// Create an AccelStepper object in DRIVER mode
AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);

void setup() {
  Serial.begin(9600);
  stepper.setMaxSpeed(500);       // Maximum speed in steps per second
  stepper.setAcceleration(1000);    // Acceleration in steps per second^2
  pinMode(homeSwitchPin, INPUT_PULLUP);
  // Enable the driver (if needed)
  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, LOW);    // LOW to enable, HIGH to disable

  // Set the initial target position
  Serial.println("Target Number Of steps = " + String(steps_command));
  stepper.moveTo(steps_command);
}

int min_position = 0;
int max_position = 1000;

void loop() {

  stepper.run();
  
  if (stepper.currentPosition()==max_position)
  {
    delay(1000);
    Serial.println("Moving to new target " + String(min_position) + " steps");
    stepper.moveTo(min_position);

  }
  else if (stepper.currentPosition()==min_position)
  {
    delay(1000);
    Serial.println("Moving to new target " + String(max_position) + " steps");
    stepper.moveTo(max_position);
  }
  
}