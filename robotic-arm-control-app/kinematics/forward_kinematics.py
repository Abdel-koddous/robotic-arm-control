print("########################################################")
print("###########   Forward Kinematics Test   ################")
print("########################################################")

import numpy as np
from roboticstoolbox import Robot
import os

cwd = os.path.dirname(os.path.abspath(__file__))
print("Current working directory:", cwd)

# Load the URDF file
URDF_FILE_PATH = os.path.join(cwd, 'urdf/mogarobot.urdf.xacro')
print("URDF file path:", URDF_FILE_PATH)
robot = Robot.URDF(URDF_FILE_PATH)
print(robot)

#q = np.array([0, 0, 0, 0, 0])
q = np.array([0.687, 1.544, -0.594, -1.002, 1.069])
T = robot.fkine(q)

print(T)
print("########################################################")
print("Input | Robot Joint Angles (radians):", q)
print("Input | Robot Joint Angles (degrees):", np.rad2deg(q))
#  Extracting Position & Orientation
print("Output | End Effector Position (x,y,z):", T.t)
#print("Rotation matrix:\n", T.R)
print("Output | End Effector Roll-Pitch-Yaw (radians):", T.rpy())
print("Output | End Effector Roll-Pitch-Yaw (degrees):", np.rad2deg(T.rpy()))