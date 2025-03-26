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


if __name__ == "__main__":

    print("########################################################")
    print("###########   Forward Kinematics Test   ################")
    print("########################################################")

    mogarobot = load_robot_urdf('mogarobot.urdf.xacro')
    #q = np.array([0, 0, 0, 0, 0])
    q = np.array([0.687, 1.544, -0.594, -1.002, 1.069])
    T = mogarobot.fkine(q)

    print(T)
    print("########################################################")
    print("Input | Robot Joint Angles (radians):", q)
    print("Input | Robot Joint Angles (degrees):", np.rad2deg(q))
    #  Extracting Position & Orientation
    print("Output | End Effector Position (x,y,z):", T.t)
    #print("Rotation matrix:\n", T.R)
    print("Output | End Effector Roll-Pitch-Yaw (radians):", T.rpy())
    print("Output | End Effector Roll-Pitch-Yaw (degrees):", np.rad2deg(T.rpy()))