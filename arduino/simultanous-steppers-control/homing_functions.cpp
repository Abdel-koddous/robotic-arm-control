#include "homing_functions.h" // Include the header file
#include <AccelStepper.h>
#include <Arduino.h> // Required for Arduino functions like digitalRead and Serial

// Declare the global variables from the main file
extern AccelStepper roboticArmSteppers[]; 
extern int limit_switchPins[]; 

// Define the homing functions
void homeBase() {
  Serial.println("Homing Base (J1)...");
  roboticArmSteppers[0].moveTo(-100000); // Clockwise
  while (digitalRead(limit_switchPins[0]) == HIGH) {
    roboticArmSteppers[0].run();
  }
  roboticArmSteppers[0].stop();
  roboticArmSteppers[0].setCurrentPosition(0);
  roboticArmSteppers[0].moveTo(300); // Back off 150 steps
  while (roboticArmSteppers[0].distanceToGo() != 0) {
    roboticArmSteppers[0].run();
  }
  roboticArmSteppers[0].moveTo(-100000);
  roboticArmSteppers[0].setMaxSpeed(100);
  roboticArmSteppers[0].setAcceleration(1000);
  while (digitalRead(limit_switchPins[0]) == HIGH) {
    roboticArmSteppers[0].run();
  }
  roboticArmSteppers[0].stop();
  roboticArmSteppers[0].setCurrentPosition(0);
  roboticArmSteppers[0].moveTo(300); // Back off 150 steps
  roboticArmSteppers[0].setMaxSpeed(500);
  roboticArmSteppers[0].setAcceleration(1000);
  while (roboticArmSteppers[0].distanceToGo() != 0) {
    roboticArmSteppers[0].run();
  }
  roboticArmSteppers[0].setCurrentPosition(0);
  
  Serial.println("Homing complete for Base (J1)");
}

void homeShoulder() {
  Serial.println("Homing Base (J2)...");
  roboticArmSteppers[1].moveTo(-100000); // Clockwise
  while (digitalRead(limit_switchPins[1]) == HIGH) {
    roboticArmSteppers[1].run();
  }
  roboticArmSteppers[1].stop();
  roboticArmSteppers[1].setCurrentPosition(0);
  roboticArmSteppers[1].moveTo(300); // Back off 150 steps
  while (roboticArmSteppers[1].distanceToGo() != 0) {
    roboticArmSteppers[1].run();
  }
  roboticArmSteppers[1].moveTo(-100000);
  roboticArmSteppers[1].setMaxSpeed(100);
  roboticArmSteppers[1].setAcceleration(1000);
  while (digitalRead(limit_switchPins[1]) == HIGH) {
    roboticArmSteppers[1].run();
  }
  roboticArmSteppers[1].stop();
  roboticArmSteppers[1].setCurrentPosition(0);
  roboticArmSteppers[1].moveTo(300); // Back off 150 steps
  roboticArmSteppers[1].setMaxSpeed(500);
  roboticArmSteppers[1].setAcceleration(1000);
  while (roboticArmSteppers[1].distanceToGo() != 0) {
    roboticArmSteppers[1].run();
  }
  roboticArmSteppers[1].setCurrentPosition(0);
  
  Serial.println("Homing complete for Base (J2)");
}

void homeElbow() {
  Serial.println("Homing Base (J3)...");
  roboticArmSteppers[2].moveTo(-100000); // Clockwise
  while (digitalRead(limit_switchPins[2]) == HIGH) {
    roboticArmSteppers[2].run();
  }
  roboticArmSteppers[2].stop();
  roboticArmSteppers[2].setCurrentPosition(0);
  roboticArmSteppers[2].moveTo(300); // Back off 150 steps
  while (roboticArmSteppers[2].distanceToGo() != 0) {
    roboticArmSteppers[2].run();
  }
  roboticArmSteppers[2].moveTo(-100000);
  roboticArmSteppers[2].setMaxSpeed(100);
  roboticArmSteppers[2].setAcceleration(1000);
  while (digitalRead(limit_switchPins[2]) == HIGH) {
    roboticArmSteppers[2].run();
  }
  roboticArmSteppers[2].stop();
  roboticArmSteppers[2].setCurrentPosition(0);
  roboticArmSteppers[2].moveTo(300); // Back off 150 steps
  roboticArmSteppers[2].setMaxSpeed(500);
  roboticArmSteppers[2].setAcceleration(1000);
  while (roboticArmSteppers[2].distanceToGo() != 0) {
    roboticArmSteppers[2].run();
  }
  roboticArmSteppers[2].setCurrentPosition(0);
  
  Serial.println("Homing complete for Base (J3)");
}

void homeWrist(){
  Serial.println("Homing Wrist (J4)...");
  roboticArmSteppers[3].moveTo(-100000); // Clockwise
  while (digitalRead(limit_switchPins[3]) == HIGH) {
    roboticArmSteppers[3].run();
  }
  roboticArmSteppers[3].stop();
  roboticArmSteppers[3].setCurrentPosition(0);
  roboticArmSteppers[3].moveTo(300); // Back off 150 steps
  while (roboticArmSteppers[3].distanceToGo() != 0) {
    roboticArmSteppers[3].run();
  }
  roboticArmSteppers[3].moveTo(-100000);
  roboticArmSteppers[3].setMaxSpeed(100);
  roboticArmSteppers[3].setAcceleration(1000);
  while (digitalRead(limit_switchPins[3]) == HIGH) {
    roboticArmSteppers[3].run();
  }
  roboticArmSteppers[3].stop();
  roboticArmSteppers[3].setCurrentPosition(0);
  roboticArmSteppers[3].moveTo(300); // Back off 150 steps
  roboticArmSteppers[3].setMaxSpeed(500);
  roboticArmSteppers[3].setAcceleration(1000);
  while (roboticArmSteppers[3].distanceToGo() != 0) {
    roboticArmSteppers[3].run();
  }
  roboticArmSteppers[3].setCurrentPosition(0);
  
  Serial.println("Homing complete for Wrist (J4)");
}

void homeAllAxes() {
  Serial.println("Homing all axes...");

  homeBase();      // Home Base (J1)
  homeShoulder();  // Home Shoulder (J2)
  homeElbow();     // Home Elbow (J3)
  homeWrist();     // Home Wrist (J4)     

  Serial.println("Homing complete for all axes");
}
