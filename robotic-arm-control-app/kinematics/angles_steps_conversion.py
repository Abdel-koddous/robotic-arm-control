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
from collections import namedtuple

def angle_to_steps(angle, gear_reduction, microstepping):
    """
    Convert an input angle to number of steps to be sent to the stepper motor.
    """
    steps_per_revolution = 200 * (1/gear_reduction) * (1/microstepping)
    steps_matching_angle = angle * steps_per_revolution / 360
    print(
        f"Angle: {angle} degrees | Gear reduction: 1/{int(1/gear_reduction)} | "
        f"Microstepping: 1/{int(1/microstepping)} => Steps: {steps_matching_angle}"
    )
    
    return steps_matching_angle


def init_joints_configs():
    """
    Initialize the joint configurations for the robotic arm with their given 
    gear reduction and microstepping values.
    """
    num_joints = 5
    JointConfig = namedtuple("JointConfig", ["gear_reduction", "microstepping"])
    joints_gear_reduction = [1/5, 1/20, 1/10, 1/3, 1/1]
    joints_microstepping = [1/4, 1/8, 1/4, 1/4, 1/16]

    joints_configs = []
    for joint_index in range(num_joints):
        gear_reduction = joints_gear_reduction[joint_index]
        microstepping = joints_microstepping[joint_index]
        joint = JointConfig(gear_reduction=gear_reduction, microstepping=microstepping)
        joints_configs.append(joint)
        print(f"Joint {joint_index}: {joint}")

    return joints_configs



if __name__ == "__main__":
    # Example 1: No gear reduction, and no microstepping (full steps)
    angle_to_steps(90, 1, 1)

    # Example 2: No gear reduction, and no microstepping (full steps)
    angle_to_steps(-180, 1, 1)

    # Example 3: Gear reduction = 1/5 and no microstepping (full steps)
    angle_to_steps(90, 1/5, 1)

    # Example 4: Gear reduction = 1/5 and microstepping = 1/4 (4 * 200 steps per revolution)
    angle_to_steps(90, 1/5, 1/4)

    # Example 5: Initialize the joint configurations
    init_joints_configs()
