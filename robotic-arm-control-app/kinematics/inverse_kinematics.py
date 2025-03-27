print("######### Inverse Kinematics Test ###########")
import numpy as np
from roboticstoolbox import Robot
import os
#from kinematics.forward_kinematics import load_robot_urdf
from spatialmath import SE3
from kinematics.forward_kinematics import load_robot_urdf

def compute_inverse_kinematics(robot, target_position, target_orientation):
    """
    Compute the inverse kinematics of the robot and generate the joint angles
    """
    # convert list to numpy array
    target_position = np.array(target_position) / 10.0
    target_orientation = np.array(target_orientation)
    print("Computing Inverse Kinematics...")
    print("target_position:", target_position)
    print("target_orientation:", target_orientation)
    target_pose = SE3(target_position) * SE3.RPY(target_orientation, unit='deg')  # Example position

    q_ik = robot.ikine_LM(target_pose) # Returns an IK solution object

    print(type(q_ik))
    for i, solution in enumerate(q_ik):
        print(f"Solutions vector element {i}: {solution}")
    print("########################################################")
    print(f"Inverse Kinematics | Input | Target Pose: Position: {target_position} Orientation: {target_orientation}")
    print(f"Inverse Kinematics | Output | Robotic arm joints angles (deg): {np.round(np.rad2deg(q_ik.q), 2)}")
    print("########################################################")

    return q_ik


if __name__ == "__main__":
    # Load the robot model
    mogarobot = load_robot_urdf()
    # Define a target pose (position and orientation)
    target_position = [20, 20, 10]
    target_orientation = [0.0, 90.0, 0.0]

    compute_inverse_kinematics(mogarobot, target_position, target_orientation)
