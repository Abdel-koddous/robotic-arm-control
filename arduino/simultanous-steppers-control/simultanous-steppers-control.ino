#include <AccelStepper.h>
#include "Servo.h"
#include "homing_functions.h"

// Define stepper motor connections and motor interface type
#define motorInterfaceType 1
#define NUMBER_OF_MOTORS 5
#define NUMBER_OF_LS 4



int steppers_dirPin[NUMBER_OF_MOTORS]  = {A1, A7, 48, 28, 34};
int steppers_stepPin[NUMBER_OF_MOTORS] = {A0, A6, 46, 26, 36};
int steppers_enabPin[NUMBER_OF_MOTORS] = {38, A2, A8, 24, 30};

int limit_switchPins[NUMBER_OF_LS] = {3, 2, 14, 15};
  

AccelStepper roboticArmSteppers[NUMBER_OF_MOTORS] = {
    AccelStepper(motorInterfaceType, steppers_stepPin[0], steppers_dirPin[0]), // Base motor
    AccelStepper(motorInterfaceType, steppers_stepPin[1], steppers_dirPin[1]), // Shoulder motor
    AccelStepper(motorInterfaceType, steppers_stepPin[2], steppers_dirPin[2]), // Elbow motor
    AccelStepper(motorInterfaceType, steppers_stepPin[3], steppers_dirPin[3]), // Wrist motor
    AccelStepper(motorInterfaceType, steppers_stepPin[4], steppers_dirPin[4])  // Hand motor
};

Servo gripperServo;
void parseInputCommand(String command) {
  if (command.startsWith("s")) {
    Serial.println("Stop command received - Stopping all motors");
    for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
      roboticArmSteppers[i].stop();
    }
  } 
  else if (command.startsWith("m")) {
    parseMultipleMoveCommands(command);
  }
  else if (command.startsWith("h")){
    homeAllAxes();
  }
  else if (command.startsWith("g")){
    processGripperCommand(command);
  }
  else
  {
    Serial.println("INVALID command received => " + command);
  }
}

void parseMultipleMoveCommands(String command) {
    //Serial.println("==========================");
    //Serial.println("ArduinoReceived=>" + command);
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

    if (motorId == 5)
    {
      // Gripper command value 
      int gripperPosition = command.substring(2).toInt();
      gripperServo.write(gripperPosition);
    }
    else
    {
      // Set target position based on direction code and steps specified in the command
      int directionCode = command.charAt(2) - '0';
      int steps = command.substring(3).toInt();

      int targetPosition = (directionCode == 0) ? steps : (directionCode == 1) ? -steps : 0;

      /*
      Serial.println("Motor ID: " + String(motorId));
      Serial.println("Direction Code: " + String(directionCode));
      Serial.println("Steps: " + String(steps));
      Serial.println("Target Position: " + String(targetPosition));
      */

      if (roboticArmSteppers[motorId].currentPosition() == targetPosition) {
        //Serial.println("Stepper " + String(motorId) + " is already at the target destination: " + String(roboticArmSteppers[motorId].currentPosition()));
        Serial.println("m" + String(motorId) + String(directionCode) + String(roboticArmSteppers[motorId].currentPosition()) + "done");

      } 
      else 
      {
        roboticArmSteppers[motorId].moveTo(targetPosition);
        //Serial.println("Stepper " +   String(motorId) + " STARTED moving...");
        Serial.println("m" + String(motorId) + String(directionCode) + String(steps) + "run");
      }
    }
  }
}

void ManageStepperMovement(AccelStepper &stepper, int stepperIndex, bool &stepperIsMovingStatus) {
  if (stepper.distanceToGo() != 0) {
      stepper.run();
      stepperIsMovingStatus = true;
  } else if (stepper.distanceToGo() == 0 && stepperIsMovingStatus == true) {
      //Serial.println("Stepper " + String(stepperIndex) + " is at the destination: " + String(stepper.currentPosition()));
      int currentPosition = stepper.currentPosition();
      if (currentPosition < 0) {
        Serial.println("m" + String(stepperIndex) + String(1) + String(abs(currentPosition)) + "done");
      } else {
        Serial.println("m" + String(stepperIndex) + String(0) + String(abs(currentPosition)) + "done");
      }
      stepperIsMovingStatus = false; 
  }
}


void processGripperCommand(String command){
  if (command.startsWith("g")){
    Serial.println("Processing gripper command => " + command);
    int gripperPosition = command.substring(1).toInt();
    gripperServo.write(gripperPosition);
  }
}



void setup() {
  Serial.begin(9600);


  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    roboticArmSteppers[i].setMaxSpeed(500);
    roboticArmSteppers[i].setAcceleration(1000);
  }
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    pinMode(steppers_enabPin[i], OUTPUT); // Set pin as output
    digitalWrite(steppers_enabPin[i], LOW); // Set pin to LOW
  }
  for (int i=0; i<NUMBER_OF_LS; i++){
  pinMode(limit_switchPins[i], INPUT_PULLUP);
  }

  gripperServo.attach(11);
  gripperServo.write(0);

  //pinMode(steppers_dirPin[0], INPUT);
  //digitalWrite(steppers_dirPin[0], HIGH);
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