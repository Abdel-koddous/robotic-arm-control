## Simultaneous Steppers Control

### Simultaneous Move Command

To use the multiple move commands on the serial link (9600 baud rate), send a command string starting with 'm' followed by the motor commands. Each motor command consists of a motor ID, a direction (not yet supported), and the number of steps. 

For example, the command `m002000m101000m201500` will:
- Move motor 0 (1st joint) clockwise for 2000 steps
- Move motor 1 (2nd joint) clockwise for 1000 steps
- Move motor 2 (3rd joint) clockwise for 1500 steps
  
Make sure to monitor the serial output for feedback on the commands being processed and the positions of the motors.

__Note 1__: For now up to 5 steppers are supported.

__Note 2__: you can also use the `m` command to move a single motor.

* Example: `m002000` will move motor 0 (1st joint) clockwise for 2000 steps.

### Stop Command
To stop all motors, send the command `s`. This will immediately stop all motor movements regardless of their current position.

