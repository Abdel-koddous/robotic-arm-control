print("######### Inverse Kinematics Test ###########")
import numpy as np
from roboticstoolbox import Robot
import os
#from forward_kinematics import load_robot_urdf
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
    print("target_position in cm/10:", target_position)
    print("target_orientation in deg:", target_orientation)
    target_pose = SE3(target_position) * SE3.RPY(target_orientation, unit='deg')  # Example position
    
    q_ik = robot.ikine_LM(target_pose) # Returns an IK solution object

    print(type(q_ik))
    for i, solution in enumerate(q_ik):
        print(f"Solutions vector element {i}: {solution}")
    print("########################################################")
    print(f"Inverse Kinematics | Input | Target Pose: Position: {target_position} Orientation: {target_orientation}")
    print(f"Inverse Kinematics | Output | Robotic arm joints angles (deg): {np.round(np.rad2deg(q_ik.q), 0)}")
    print("########################################################")

    return q_ik


if __name__ == "__main__":
    # Load the robot model
    mogarobot = load_robot_urdf()
    # Define a target pose (position and orientation)
    target_position = [22, -10, 8]
    target_orientation = [0.0, 120, 0.0]

    list_of_solutions = []
    compute_rounds = 10
    for i in range(compute_rounds):
        solution_ik = compute_inverse_kinematics(mogarobot, target_position, target_orientation)
        solution_ik_rounded = np.round(np.rad2deg(solution_ik.q), 0)
        list_of_solutions.append(solution_ik_rounded)

    # print unique solutions
    unique_solutions = np.unique(list_of_solutions, axis=0)
    for i, solution in enumerate(unique_solutions):
        print(f"Unique solution {i}: {solution}")
    print("########################################################")
    for i, solution in enumerate(unique_solutions):
        print(f"Unique solution {i}: {np.round(np.radians(solution), 2)}")
