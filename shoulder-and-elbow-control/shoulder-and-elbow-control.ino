#include <AccelStepper.h>

// Pin assignments
const int elbow_stepPin = 2;
const int elbow_dirPin = 3;
const int shoudler_stepPin = 4;     // Connects to STEP on the driver
const int shoulder_dirPin = 5;      // Connects to DIR on the driver
const int base_stepPin = 6;
const int base_dirPin = 7;

const int enablePin = 5;   // Optional: Connects to ENABLE on the driver
const int homeSwitchPin = 7;

// Create an AccelStepper object in DRIVER mode
AccelStepper elbow_stepper(AccelStepper::DRIVER, elbow_stepPin, elbow_dirPin);
AccelStepper shoulder_stepper(AccelStepper::DRIVER, shoudler_stepPin, shoulder_dirPin);
AccelStepper base_stepper(AccelStepper::DRIVER, base_stepPin, base_dirPin);

int elbow_min_position = 0;
int elbow_max_position = 5000;

int shoulder_min_position = 0;
int shoulder_max_position = 3000;

int base_min_position = 0;
int base_max_position = 4500;

int step_increments = 0;

void setup() {
  Serial.begin(9600);
  shoulder_stepper.setMaxSpeed(500);       // Maximum speed in steps per second
  shoulder_stepper.setAcceleration(1000);    // Acceleration in steps per second^2

  elbow_stepper.setMaxSpeed(500);       // Maximum speed in steps per second
  elbow_stepper.setAcceleration(1000);    // Acceleration in steps per second^2
  
  base_stepper.setMaxSpeed(500);       // Maximum speed in steps per second
  base_stepper.setAcceleration(1000);    // Acceleration in steps per second^2

  pinMode(homeSwitchPin, INPUT_PULLUP);
  // Enable the driver (if needed)
  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, LOW);    // LOW to enable, HIGH to disable
  // Set the initial target position
  // Serial.println("Shoulder Target Number Of steps = " + String(shoulder_max_position));
  /*shoulder_stepper.moveTo(shoulder_max_position);
  elbow_stepper.moveTo(elbow_max_position);
  base_stepper.moveTo(base_max_position);*/

  // Wait for the serial port to be available
  while (!Serial) {
    ; // Wait for the serial port to be ready
  }
  // Prompt the user for a command
  Serial.println("Enter 'go' to begin the program."); 
  
}

int stepper_manage_range_of_motion(AccelStepper &stepper_type, int min_pos, int max_pos)
{
  int result = -1;
  
  if (stepper_type.currentPosition()==max_pos)
  {
    result = max_pos;
    //Serial.println("Stepper max position reached at " + String(result) + " steps");
    stepper_type.moveTo(min_pos);

  }
  else if (stepper_type.currentPosition()==min_pos)
  {
    result = min_pos;
    //Serial.println("Stepper min position reached at " + String(result) + " steps");
    stepper_type.moveTo(max_pos);
  } 

  return result;
}

void parseMoveCommand(String move_command, int * commands_params)
{

  commands_params[1] = move_command.substring(1, 2).toInt();  // Joint id
  commands_params[2] = move_command.substring(2, 3).toInt();; // Direction (clockwise | counter clockwise) - NOT MANAGED YET
  commands_params[3] = move_command.substring(3).toInt();;    // Nb of steps

  Serial.println("Joint ID = " + String(commands_params[1]));
  Serial.println("MOVE Direction = " + String(commands_params[2]) + " Not yet managed...");
  Serial.println("Nb of Steps = " + String(commands_params[3]));
}

String checkUserSerialInput(String current_command, int command_parameters[4])
{
  String new_command = "none";
  /*
  for (int param_index = 0; param_index < 4; param_index++)
  {
    command_parameters[param_index] = 0xffff; // Initialize command parameters with default dirty value
  }
  */

  // Check if there is data available to read from the serial port
  if (Serial.available() > 0) 
  {
    // Read the input from the user
    String userInput = Serial.readStringUntil('\n');  // Read until the user presses Enter
    // Trim any extra spaces or newlines
    userInput.trim();
    // If the user enters 'start', proceed to the main program
    if (userInput == "go") 
    {
      new_command = "go";
      command_parameters[0] = 0;
      Serial.println("GO Command received (go). Starting the robotic arm...");
    } 
    else if (userInput == "s")
    {
      new_command = "stop";
      command_parameters[0] = 1;
      Serial.println("STOP Command received (s). Stopping the robotic arm...");
    }
    else if (userInput.substring(0, 1) == "m")
    {
      new_command = "move";
      Serial.println("Joints MOVE Command received (" + userInput + "). Moving Joint...");
      command_parameters[0] = 2;
      parseMoveCommand(userInput, command_parameters);
    }
    else
    {
      Serial.println("UNKNOW Command received (" + userInput + ")...");
    }
  }
  else
  {
    // No new command detected
    new_command = current_command;
  }

  return new_command;

}
int joint_id = -1; // 0 = base, 1 = shoulder, 2 = elbow, 3 = gripper
String current_command = "stop";
int new_command_params[4];  // Declare an array of size 4
bool stepper_started = false;
  

void loop() {

  String new_command = checkUserSerialInput(current_command, new_command_params);

  if (new_command == "move")
  {
    joint_id = new_command_params[1];
    int direction = (new_command_params[2] == 0) ? 1 : -1; // 
    int target_position = new_command_params[3];

    switch (joint_id) {
      case 0:
        if (stepper_started == false)
        {
          base_stepper.moveTo(direction * target_position); // Nb of Steps in the specified direction
          stepper_started = true;
          base_stepper.run();
          Serial.println("base_stepper STARTED with target position : " + String(target_position));
        }
        else
        {
          base_stepper.run();
          if (base_stepper.currentPosition() == target_position)
          {
            Serial.println("base_stepper REACHED target position " + String(target_position));
            stepper_started = false;
            new_command = "stop";
          }
        }
        break;

      case 1:
        if (stepper_started == false)
        {
          shoulder_stepper.moveTo(target_position); // Nb of Steps in the specified direction
          stepper_started = true;
          shoulder_stepper.run();
          Serial.println("shoulder_stepper STARTED with target position : " + String(target_position));
        }
        else
        {
          shoulder_stepper.run();
          if (shoulder_stepper.currentPosition() == target_position)
          {
            Serial.println("shoulder_stepper REACHED target position " + String(target_position));
            stepper_started = false;
            new_command = "stop";
          }
        }
        break;

        case 2:
        if (stepper_started == false)
        {
          elbow_stepper.moveTo(target_position); // Nb of Steps in the specified direction
          stepper_started = true;
          elbow_stepper.run();
          Serial.println("elbow_stepper STARTED with target position : " + String(target_position));
        }
        else
        {
          elbow_stepper.run();
          if (elbow_stepper.currentPosition() == target_position)
          {
            Serial.println("elbow_stepper REACHED target position " + String(target_position));
            stepper_started = false;
            new_command = "stop";
          }
        }
        break;
    }    

  }

  current_command = new_command;
}
