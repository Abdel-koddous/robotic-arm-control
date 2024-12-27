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
  shoulder_stepper.moveTo(shoulder_max_position);
  elbow_stepper.moveTo(elbow_max_position);
  base_stepper.moveTo(base_max_position);

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

int motionPlanningStep = 1;
String currentCommand = "stop";
void loop() {

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
      currentCommand = "go";
      Serial.println("GO Command received (go). Starting the robotic arm...");
    } 
    else if (userInput == "s")
    {
      currentCommand = "stop";
      Serial.println("STOP Command received (s). Stopping the robotic arm...");
    }
  }

  if (currentCommand == "go")
  {
    int motion_result = -1;

    // Motion Planning Sequence
    

    switch (motionPlanningStep) {
      case 1:
        shoulder_stepper.run();
        motion_result = stepper_manage_range_of_motion(shoulder_stepper, shoulder_min_position, shoulder_max_position);
        if (motion_result == shoulder_max_position)
        {
          motionPlanningStep = 2;
          Serial.println("Next Step in Motion Planning Sequence = " + String(motionPlanningStep));
        }
        break;

      case 2:
        base_stepper.run();
        motion_result = stepper_manage_range_of_motion(base_stepper, base_min_position, base_max_position);
        if (motion_result == base_max_position || motion_result == base_min_position)
        {
          motionPlanningStep = 1;
          Serial.println("Next Step in Motion Planning Sequence = " + String(motionPlanningStep));
        }
        break;

      /*
      case 3:
        shoulder_stepper.run();
        motion_result = stepper_manage_range_of_motion(shoulder_stepper, shoulder_min_position, shoulder_max_position);
        if (motion_result == shoulder_min_position)
        {
          motionPlanningStep = 4;
          Serial.println("Next Step in Motion Planning Sequence = " + String(motionPlanningStep));
        }
        break;

      case 4:
        shoulder_stepper.run();
        motion_result = stepper_manage_range_of_motion(shoulder_stepper, shoulder_min_position, shoulder_max_position);
        if (motion_result == shoulder_max_position)
        {
          motionPlanningStep = 5;
          Serial.println("Next Step in Motion Planning Sequence = " + String(motionPlanningStep));
        }
        break;

      case 5:
        base_stepper.run();
        motion_result = stepper_manage_range_of_motion(base_stepper, base_min_position, base_max_position);
        if (motion_result == base_min_position)
        {
          motionPlanningStep = 6;
          Serial.println("Next Step in Motion Planning Sequence = " + String(motionPlanningStep));
        }
        break;

      case 6:
        shoulder_stepper.run();
        motion_result = stepper_manage_range_of_motion(shoulder_stepper, shoulder_min_position, shoulder_max_position);
        if (motion_result == shoulder_min_position)
        {
          motionPlanningStep = 1;
          Serial.println("Next Step in Motion Planning Sequence = " + String(motionPlanningStep));
        }
        break;


      default:
        // if nothing else matches, do the default
        Serial.println("motionPlanningStep NOT HANDLED PROPERLY...");
        break;
      */
    }    

    //elbow_stepper.run();  
    //stepper_manage_range_of_motion(elbow_stepper, elbow_min_position, elbow_max_position);
  }


}
