"""
This module contains conversion functions between joint angles and stepper motor steps.
The conversion is a function of the gear ratio and microstepping parameters 
for each stepper motor/joint.

Examples:
- No gear reduction, and no microstepping (full steps)
* 1 full revolution = 360 degrees = 200 steps
* 1 step = 360 degrees / 200 steps = 1.8 degrees

- Gear reduction = 1/5 and no microstepping (full steps )
* 1 full revolution = 360 degrees = 200 steps * 5 = 1000 steps
* 1 step = 360 degrees / 1000 steps = 0.36 degrees

- Gear reduction = 1/5 and microstepping = 1/4 (4 * 200 steps per revolution)
* 1 full revolution = 360 degrees = 4 * 200 steps * 5 = 4000 steps
* 1 step = 360 degrees / 4000 steps = 0.09 degrees

"""

def angle_to_steps(angle, gear_reduction, microstepping):
    """Convert an input angle to number of steps to be sent to the stepper motor."""
    steps_per_revolution = 200 * (1/gear_reduction) * (1/microstepping)
    steps_matching_angle = angle * steps_per_revolution / 360
    print(f"Angle: {angle} degrees | Gear reduction: 1/{int(1/gear_reduction)} | Microstepping: 1/{int(1/microstepping)} => Steps: {steps_matching_angle}")
    return steps_matching_angle


if __name__ == "__main__":
    # Example 1: No gear reduction, and no microstepping (full steps)
    angle_to_steps(90, 1, 1)
  
    # Example 2: No gear reduction, and no microstepping (full steps)
    angle_to_steps(-180, 1, 1)

    # Example 3: Gear reduction = 1/5 and no microstepping (full steps)
    angle_to_steps(90, 1/5, 1)

    # Example 4: Gear reduction = 1/5 and microstepping = 1/4 (4 * 200 steps per revolution)
    angle_to_steps(90, 1/5, 1/4)

