#include <AccelStepper.h>

// Define stepper motor connections and motor interface type
#define motorInterfaceType 1
AccelStepper stepper1(motorInterfaceType, 3, 2); // Base motor (1st joint)
AccelStepper stepper2(motorInterfaceType, 5, 4); // Shoulder motor (2nd joint)


void parseInputCommand(String command)
{
  /*
  * This function is used to parse the input command and execute the appropriate actions for the stepper motors. 
  * Current supported commands:
  * - 's': Stop command. Stops all motors immediately.
  * - 'm': Move command. Initiates movement for specified motors based on the sub-commands.
  */
  if (command.startsWith("s"))
  {
    Serial.println("Stop command received - Stopping all motors");
    stepper1.stop();
    stepper2.stop();
  }
  else if (command.startsWith("m"))
  {
    parseMultipleMoveCommands(command);
  }
}

void parseMultipleMoveCommands(String command)
{
    /*
    * This function is used to parse the move command of multiple motors and extract the sub-commands
    * Example : m002000m101000m201500 input will be split into 3 sub-commands : m002000, m101000, m201500
    */
    Serial.println("================================================");
    Serial.println("Parsing input command: " + command);
    // Split the command into individual sub-commands
    int separatorIndex = 0;
    while (separatorIndex < command.length()) {
        int nextSeparatorIndex = command.indexOf('m', separatorIndex + 1);
        String subCommand;
        
        if (nextSeparatorIndex == -1) {
            subCommand = command.substring(separatorIndex); // Get the last sub-command
            separatorIndex = command.length(); // Exit the loop
        } else {
            subCommand = command.substring(separatorIndex, nextSeparatorIndex); // Get the sub-command
            separatorIndex = nextSeparatorIndex; // Move to the next 'm'
        }
        Serial.println("Sub-command received: " + subCommand);
        processCommand(subCommand);
    }
}

void processCommand(String command) {
  
  /* 
  * This is a non-blocking function to process the steppers move command 
  * Can be used to move multiple motors simultaneously 
  * Example command format: m002000 (1st joint, clockwise, 2000 steps)
  * Example command format: m101000 (2nd joint, clockwise, 1000 steps)
  */

  if (command.startsWith("m")) {
    Serial.println("Processing command: " + command);
    int motorId = command.charAt(1) - '0'; // Get motor ID (0 or 1)
    int direction = command.charAt(2) - '0'; // Get direction (0 = clockwise, 1 = counter-clockwise)
    int steps = command.substring(3).toInt(); // Get number of steps

    Serial.println("Motor ID: " + String(motorId));
    Serial.println("Direction: " + String(direction));
    Serial.println("Steps: " + String(steps));

    // Move the appropriate motor
    if (motorId == 0) {
      stepper1.moveTo(steps); // Move stepper 1
    } else if (motorId == 1) {
      stepper2.moveTo(steps); // Move stepper 2
    }
  }
}

void setup() {
  Serial.begin(9600); // Start serial communication
  stepper1.setMaxSpeed(500); // Set maximum speed for stepper 1
  stepper1.setAcceleration(1000); // Set acceleration for stepper 1
  stepper2.setMaxSpeed(500); // Set maximum speed for stepper 2
  stepper2.setAcceleration(1000); // Set acceleration for stepper 2
}

// Array to store the state of the steppers
bool stepperIsMoving[2] = {false, false};

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read command until newline    
    parseInputCommand(command); // Process the command
  }
  else
  {
    // Move both motors simultaneously
    if (stepper1.distanceToGo() != 0)
    {
      stepper1.run();
      stepperIsMoving[0] = true;
    }
    else if (stepperIsMoving[0] == true)
    {
      Serial.println("Stepper 1 is at the destination :" + String(stepper1.currentPosition()));
      stepperIsMoving[0] = false;
    }
    
    if (stepper2.distanceToGo() != 0)
    {
      stepper2.run();
      stepperIsMoving[1] = true;
    }
    else if (stepperIsMoving[1] == true)
    {
      Serial.println("Stepper 2 is at the destination :" + String(stepper2.currentPosition()));
      stepperIsMoving[1] = false;
    }
  }
}