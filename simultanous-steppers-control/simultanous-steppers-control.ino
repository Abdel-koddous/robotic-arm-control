#include <AccelStepper.h>

// Define stepper motor connections and motor interface type
#define motorInterfaceType 1
AccelStepper stepper1(motorInterfaceType, 3, 2); // Base motor (1st joint)
AccelStepper stepper2(motorInterfaceType, 5, 4); // Shoulder motor (2nd joint)

void setup() {
  Serial.begin(9600); // Start serial communication
  stepper1.setMaxSpeed(500); // Set maximum speed for stepper 1
  stepper1.setAcceleration(1000); // Set acceleration for stepper 1
  stepper2.setMaxSpeed(500); // Set maximum speed for stepper 2
  stepper2.setAcceleration(1000); // Set acceleration for stepper 2
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read command until newline
    
    //processCommand(command); // Process the command
    parseMultipleMoveCommands(command);
  }
  else
  {
    stepper1.run(); // Run the stepper 1
    stepper2.run(); // Run the stepper 2
  }
}

void parseMultipleMoveCommands(String command)
{
    /*
    This function is used to parse the move command of multiple motors and extract the sub-commands
    Example : m002000m101000m201500 input will be parsed into 3 sub-commands : m002000, m101000, m201500
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
  // Example command format: m002000 (1st joint, clockwise, 2000 steps)
  if (command.startsWith("m")) {

    Serial.println("Processing command: " + command);
    int motorId = command.charAt(1) - '0'; // Get motor ID (0 or 1)
    int direction = command.charAt(2) - '0'; // Get direction (0 = clockwise, 1 = counter-clockwise)
    int steps = command.substring(3).toInt(); // Get number of steps

    Serial.println("Motor ID: " + String(motorId));
    Serial.println("Direction: " + String(direction));
    Serial.println("Steps: " + String(steps));

    // Adjust steps based on direction
    //if (direction == 1) {
    //  steps = -steps; // Reverse steps for counter-clockwise
    //}

    // Move the appropriate motor
    if (motorId == 0) {
      stepper1.moveTo(steps); // Move stepper 1
    } else if (motorId == 1) {
      stepper2.moveTo(steps); // Move stepper 2
    }

    // Move both motors simultaneously
    if (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0)
    {
      stepper1.run();
      stepper2.run();
    }
  }
}