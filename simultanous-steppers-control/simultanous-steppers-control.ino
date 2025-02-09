#include <AccelStepper.h>

// Define stepper motor connections and motor interface type
#define motorInterfaceType 1
int steppers_dirPin[5]  = {2, 4, 6, 8, 10};
int steppers_stepPin[5] = {3, 5, 7, 9, 11};

AccelStepper stepper1(motorInterfaceType, steppers_stepPin[0], steppers_dirPin[0]); // Base motor
AccelStepper stepper2(motorInterfaceType, steppers_stepPin[1], steppers_dirPin[1]); // Shoulder motor
AccelStepper stepper3(motorInterfaceType, steppers_stepPin[2], steppers_dirPin[2]); // Elbow motor
AccelStepper stepper4(motorInterfaceType, steppers_stepPin[3], steppers_dirPin[3]); // Wrist motor
AccelStepper stepper5(motorInterfaceType, steppers_stepPin[4], steppers_dirPin[4]); // Hand motor

void parseInputCommand(String command) {
  if (command.startsWith("s")) {
    Serial.println("Stop command received - Stopping all motors");
    stepper1.stop(); stepper2.stop(); stepper3.stop(); stepper4.stop(); stepper5.stop();
  } else if (command.startsWith("m")) {
    parseMultipleMoveCommands(command);
  }
}

void parseMultipleMoveCommands(String command) {
    Serial.println("================================================");
    Serial.println("Parsing input command: " + command);
    int separatorIndex = 0;
    while (separatorIndex < command.length()) {
        int nextSeparatorIndex = command.indexOf('m', separatorIndex + 1);
        String subCommand;
        
        if (nextSeparatorIndex == -1) {
            subCommand = command.substring(separatorIndex);
            separatorIndex = command.length();
        } else {
            subCommand = command.substring(separatorIndex, nextSeparatorIndex);
            separatorIndex = nextSeparatorIndex;
        }
        Serial.println("Sub-command received: " + subCommand);
        processCommand(subCommand);
    }
}

void processCommand(String command) {
  if (command.startsWith("m")) {
    Serial.println("Processing command: " + command);
    int motorId = command.charAt(1) - '0';
    int direction = command.charAt(2) - '0';
    int steps = command.substring(3).toInt();

    Serial.println("Motor ID: " + String(motorId));
    Serial.println("Direction: " + String(direction));
    Serial.println("Steps: " + String(steps));

    if (motorId == 0) {
      stepper1.moveTo(steps);
    } else if (motorId == 1) {
      stepper2.moveTo(steps);
    } else if (motorId == 2) {
      stepper3.moveTo(steps);
    } else if (motorId == 3) {
      stepper4.moveTo(steps);
    } else if (motorId == 4) {
      stepper5.moveTo(steps);
    }
    Serial.println("Stepper STARTED moving...");
  }
}

void ManageStepperMovement(AccelStepper &stepper, int stepperIndex, bool &stepperIsMovingStatus) {
  if (stepper.distanceToGo() != 0) {
      stepper.run();
      stepperIsMovingStatus = true;
  } else if (stepper.distanceToGo() == 0 && stepperIsMovingStatus == true) {
      Serial.println("Stepper " + String(stepperIndex + 1) + " is at the destination: " + String(stepper.currentPosition()));
      stepperIsMovingStatus = false; 
  }
}

void setup() {
  Serial.begin(9600);
  stepper1.setMaxSpeed(500); stepper1.setAcceleration(1000);
  stepper2.setMaxSpeed(500); stepper2.setAcceleration(1000);
  stepper3.setMaxSpeed(500); stepper3.setAcceleration(1000);
  stepper4.setMaxSpeed(500); stepper4.setAcceleration(1000);
  stepper5.setMaxSpeed(500); stepper5.setAcceleration(1000);
}

bool stepperIsMoving[5] = {false, false, false, false, false};

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    parseInputCommand(command);
  } else {
    ManageStepperMovement(stepper1, 0, stepperIsMoving[0]);
    ManageStepperMovement(stepper2, 1, stepperIsMoving[1]);
    ManageStepperMovement(stepper3, 2, stepperIsMoving[2]);
    ManageStepperMovement(stepper4, 3, stepperIsMoving[3]);
    ManageStepperMovement(stepper5, 4, stepperIsMoving[4]);
  }
}
