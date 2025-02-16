#include <AccelStepper.h>

// Define stepper motor connections and motor interface type
#define motorInterfaceType 1
#define NUMBER_OF_MOTORS 5
int steppers_dirPin[NUMBER_OF_MOTORS]  = {2, 4, 6, 8, 10};
int steppers_stepPin[NUMBER_OF_MOTORS] = {3, 5, 7, 9, 11};

AccelStepper roboticArmSteppers[NUMBER_OF_MOTORS] = {
    AccelStepper(motorInterfaceType, steppers_stepPin[0], steppers_dirPin[0]), // Base motor
    AccelStepper(motorInterfaceType, steppers_stepPin[1], steppers_dirPin[1]), // Shoulder motor
    AccelStepper(motorInterfaceType, steppers_stepPin[2], steppers_dirPin[2]), // Elbow motor
    AccelStepper(motorInterfaceType, steppers_stepPin[3], steppers_dirPin[3]), // Wrist motor
    AccelStepper(motorInterfaceType, steppers_stepPin[4], steppers_dirPin[4])  // Hand motor
};

void parseInputCommand(String command) {
  if (command.startsWith("s")) {
    Serial.println("Stop command received - Stopping all motors");
    for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
      roboticArmSteppers[i].stop();
    }
  } else if (command.startsWith("m")) {
    parseMultipleMoveCommands(command);
  }
}

void parseMultipleMoveCommands(String command) {
    Serial.println("================================================");
    Serial.println("InputCommand => " + command);
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
        //Serial.println("Sub-command received: " + subCommand);
        processCommand(subCommand);
    }
}

void processCommand(String command) {
  if (command.startsWith("m")) {
    int motorId = command.charAt(1) - '0';
    int direction = command.charAt(2) - '0';
    int steps = command.substring(3).toInt();

    Serial.println("Motor ID: " + String(motorId));
    Serial.println("Direction: " + String(direction));
    Serial.println("Steps: " + String(steps));

    if (roboticArmSteppers[motorId].currentPosition() == steps) {
      //Serial.println("Stepper " + String(motorId) + " is already at the target destination: " + String(roboticArmSteppers[motorId].currentPosition()));
      Serial.println("m" + String(motorId) + String(roboticArmSteppers[motorId].currentPosition()) + "done");
    } 
    else 
    {
      roboticArmSteppers[motorId].moveTo(steps);
      //Serial.println("Stepper " +   String(motorId) + " STARTED moving...");
      Serial.println("m" + String(motorId) + String(direction) + String(steps) + "run");
    }
  }
}

void ManageStepperMovement(AccelStepper &stepper, int stepperIndex, bool &stepperIsMovingStatus) {
  if (stepper.distanceToGo() != 0) {
      stepper.run();
      stepperIsMovingStatus = true;
  } else if (stepper.distanceToGo() == 0 && stepperIsMovingStatus == true) {
      //Serial.println("Stepper " + String(stepperIndex) + " is at the destination: " + String(stepper.currentPosition()));
      Serial.println("m" + String(stepperIndex) + String(stepper.currentPosition()) + "done");
      stepperIsMovingStatus = false; 
  }
}

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    roboticArmSteppers[i].setMaxSpeed(500);
    roboticArmSteppers[i].setAcceleration(1000);
  }
}

bool stepperIsMoving[5] = {false, false, false, false, false};

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    parseInputCommand(command);
  } else {
    for (int stepperIndex = 0; stepperIndex < NUMBER_OF_MOTORS; stepperIndex++) {
      ManageStepperMovement(roboticArmSteppers[stepperIndex], stepperIndex, stepperIsMoving[stepperIndex]);
    }
  }
}
