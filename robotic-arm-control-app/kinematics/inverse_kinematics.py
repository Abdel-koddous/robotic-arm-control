print("######### Inverse Kinematics Test ###########")
import numpy as np
from roboticstoolbox import Robot
import os
from forward_kinematics import load_robot_urdf
from spatialmath import SE3

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
    for solution in q_ik:
        print("solution:", solution)
    print("########################################################")
    print("Inverse Kinematics | Input | Target Pose:", target_pose.t)
    print("Inverse Kinematics | Output | Robotic arm joints angles (deg):", np.round(np.rad2deg(q_ik.q), 2))
    print("########################################################")


if __name__ == "__main__":
    # Load the robot model
    mogarobot = load_robot_urdf()
    # Define a target pose (position and orientation)
    target_position = [0, 0, 0]
    target_orientation = [0.0, 0.0, 90]

    compute_inverse_kinematics(mogarobot, target_position, target_orientation)
