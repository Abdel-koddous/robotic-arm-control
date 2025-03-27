import numpy as np
from roboticstoolbox import Robot
import os


def load_robot_urdf(urdf_filename='mogarobot.urdf.xacro'):
    """
    Load the URDF file and return the robot object
    """
    # Load the URDF file
    cwd = os.path.dirname(os.path.abspath(__file__))
    urdf_full_path = os.path.join(cwd, 'urdf', urdf_filename)
    print("URDF file path:", urdf_full_path)
    print("Loading Robot from URDF file...")
    robot = Robot.URDF(urdf_full_path)
    print(robot)
    return robot

def compute_forward_kinematics(robot_model, input_joint_angles, unit='deg'):
    """
    Calculate the forward kinematics of the robot
    """
    if unit == 'deg':
        input_joint_angles_deg = np.deg2rad(input_joint_angles)
        transform_matrix = robot_model.fkine(input_joint_angles_deg)
    elif unit == 'rad':
        transform_matrix = robot_model.fkine(input_joint_angles)
    else:
        print(f"Invalid unit: {unit}")
        transform_matrix = None

    #print(f"Transform Matrix:\n{transform_matrix}")
    print("########################################################")
    print(f"Forward Kinematics | Input  | Robot Joint Angles ({unit}):", input_joint_angles)
    #  Extracting Position & Orientation
    end_effector_position = np.round(transform_matrix.t*10, 2)
    print(f"Forward Kinematics | Output | End Effector Position (x,y,z): {end_effector_position}")
    print(f"Forward Kinematics | Output | End Effector Roll-Pitch-Yaw ({unit}): {np.rad2deg(transform_matrix.rpy())}")
    print("########################################################")
    
    return transform_matrix


if __name__ == "__main__":

    print("########################################################")
    print("###########   Forward Kinematics Test   ################")
    print("########################################################")

    mogarobot = load_robot_urdf('mogarobot.urdf.xacro')
    #q = np.array([0, 0, 0, 0, 0])
    q = np.array([0.687, 1.544, -0.594, -1.002, 1.069])

    compute_forward_kinematics(mogarobot, q, unit='rad')
