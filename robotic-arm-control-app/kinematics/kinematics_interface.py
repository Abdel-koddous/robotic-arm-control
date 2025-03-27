"""
This module provides the user interface for robot arm kinematics calculations.
It allows users to perform forward and inverse kinematics for the robot arm.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QPushButton, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
import numpy as np
from kinematics.inverse_kinematics import compute_inverse_kinematics

from roboticstoolbox import Robot
from spatialmath import SE3
ROBOTICS_TOOLBOX_AVAILABLE = True

# Import the forward_kinematics module (contains fallback implementation)
from kinematics.forward_kinematics import compute_forward_kinematics

class KinematicsInterface(QWidget):
    """
    Interface for performing inverse and forward kinematics calculations.
    """
    def __init__(self, parent=None, robot=None, joint_values=None, set_joints_callback=None):
        """
        Initialize the kinematics interface.
        
        Args:
            parent: Parent widget
            robot: Robot model for kinematics calculations
            joint_values: Reference to the current joint values
            set_joints_callback: Callback function to update main app joint values
        """
        super().__init__(parent)
        self.robot = robot
        self.joint_values = joint_values
        self.set_joints_callback = set_joints_callback
        
        # End effector current position/orientation (will be updated by forward kinematics)
        self.current_position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.current_orientation = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        
        # Target position/orientation for inverse kinematics
        self.target_position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.target_orientation = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        
        # Units
        self.angle_unit = "deg"  # "deg" or "rad"
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Add warning if roboticstoolbox is not available
        if not ROBOTICS_TOOLBOX_AVAILABLE:
            warning_label = QLabel("NOTE: roboticstoolbox not available. Using simplified kinematics calculations.")
            warning_label.setStyleSheet("color: orange; font-weight: bold;")
            main_layout.addWidget(warning_label)
        
      
        # Inverse Kinematics Section
        ik_group = QGroupBox("Inverse Kinematics")
        ik_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: white;
            }
        """)
        ik_layout = QVBoxLayout()
        
        # Target position input (for inverse kinematics)
        target_group = QGroupBox("Target End Effector Position")
        target_layout = QGridLayout()
        
        # X, Y, Z Target Position
        target_layout.addWidget(QLabel("X:"), 0, 0)
        self.x_target = QLineEdit("0.0")
        target_layout.addWidget(self.x_target, 0, 1)
        
        target_layout.addWidget(QLabel("Y:"), 1, 0)
        self.y_target = QLineEdit("0.0")
        target_layout.addWidget(self.y_target, 1, 1)
        
        target_layout.addWidget(QLabel("Z:"), 2, 0)
        self.z_target = QLineEdit("0.0")
        target_layout.addWidget(self.z_target, 2, 1)
        
        # Roll, Pitch, Yaw Target Orientation
        target_layout.addWidget(QLabel("Roll:"), 0, 2)
        self.roll_target = QLineEdit("0.0")
        target_layout.addWidget(self.roll_target, 0, 3)
        
        target_layout.addWidget(QLabel("Pitch:"), 1, 2)
        self.pitch_target = QLineEdit("0.0")
        target_layout.addWidget(self.pitch_target, 1, 3)
        
        target_layout.addWidget(QLabel("Yaw:"), 2, 2)
        self.yaw_target = QLineEdit("0.0")
        target_layout.addWidget(self.yaw_target, 2, 3)
        
        # Set target to current position button
        set_target_button = QPushButton("Set Target to Current Position")
        set_target_button.clicked.connect(self.set_target_to_current)
        target_layout.addWidget(set_target_button, 3, 0, 1, 4)
        
        target_group.setLayout(target_layout)
        ik_layout.addWidget(target_group)
        
        # IK solutions display
        solutions_group = QGroupBox("IK Solutions")
        solutions_layout = QVBoxLayout()
        
        # Display area for joint solutions (to be filled by the IK calculation)
        self.solutions_display = QLabel("No solutions calculated yet.")
        solutions_layout.addWidget(self.solutions_display)
        
        solutions_group.setLayout(solutions_layout)
        ik_layout.addWidget(solutions_group)
        
        # Angle units selection
        units_layout = QHBoxLayout()
        units_layout.addWidget(QLabel("Angle Units:"))
        
        self.deg_radio = QRadioButton("Degrees")
        self.deg_radio.setChecked(True)
        self.deg_radio.toggled.connect(self.update_angle_unit)
        units_layout.addWidget(self.deg_radio)
        
        self.rad_radio = QRadioButton("Radians")
        self.rad_radio.toggled.connect(self.update_angle_unit)
        units_layout.addWidget(self.rad_radio)
        
        units_group = QButtonGroup(self)
        units_group.addButton(self.deg_radio)
        units_group.addButton(self.rad_radio)
        
        ik_layout.addLayout(units_layout)
        
        # Calculate IK button
        calculate_ik_button = QPushButton("Calculate Inverse Kinematics")
        calculate_ik_button.clicked.connect(self.calculate_inverse_kinematics)
        ik_layout.addWidget(calculate_ik_button)
        
        # Apply solution button
        apply_solution_button = QPushButton("Apply Solution to Joints")
        apply_solution_button.clicked.connect(self.apply_ik_solution)
        ik_layout.addWidget(apply_solution_button)
        
        ik_group.setLayout(ik_layout)
        main_layout.addWidget(ik_group)
        
        # Finalize layout
        self.setLayout(main_layout)
    
    def update_angle_unit(self):
        """Update the angle unit based on radio button selection."""
        if self.deg_radio.isChecked():
            self.angle_unit = "deg"
        else:
            self.angle_unit = "rad"
        
        # Recalculate displayed values if needed
        self.calculate_forward_kinematics()
    
    def calculate_forward_kinematics(self):
        """Calculate forward kinematics using the robot model and current joint values."""
        if self.joint_values:
            try:
                # Use the forward_kinematics module to calculate
                result = compute_forward_kinematics(self.robot, self.joint_values, unit=self.angle_unit)
                
                if result:
                    # Extract position and orientation
                    self.current_position = result['position']
                    self.current_orientation = result['orientation']
                    
                    # Update display
                    self.update_position_display()
                    
                    print(f"Forward kinematics calculated for joint values: {self.joint_values}")
                else:
                    self.solutions_display.setText("Error calculating forward kinematics.")
            except Exception as e:
                self.solutions_display.setText(f"Error calculating forward kinematics: {str(e)}")
                print(f"Error in forward kinematics: {e}")
        else:
            self.solutions_display.setText("Joint values not available.")
    
    def update_position_display(self):
        """Update the displayed position and orientation."""
        # Position
        self.x_position.setText(f"{self.current_position['x']:.2f}")
        self.y_position.setText(f"{self.current_position['y']:.2f}")
        self.z_position.setText(f"{self.current_position['z']:.2f}")
        
        # Orientation
        self.roll_orientation.setText(f"{self.current_orientation['roll']:.2f}")
        self.pitch_orientation.setText(f"{self.current_orientation['pitch']:.2f}")
        self.yaw_orientation.setText(f"{self.current_orientation['yaw']:.2f}")
    
    def set_target_to_current(self):
        """Set the target position/orientation to the current values."""
        # Copy current position to target fields
        self.x_target.setText(self.x_position.text())
        self.y_target.setText(self.y_position.text())
        self.z_target.setText(self.z_position.text())
        
        self.roll_target.setText(self.roll_orientation.text())
        self.pitch_target.setText(self.pitch_orientation.text())
        self.yaw_target.setText(self.yaw_orientation.text())
        
        # Update target values
        self.target_position = self.current_position.copy()
        self.target_orientation = self.current_orientation.copy()
    
    def calculate_inverse_kinematics(self):
        """Calculate inverse kinematics for the given target."""
        try:
            # Get target values from input fields
            self.target_position["x"] = float(self.x_target.text())
            self.target_position["y"] = float(self.y_target.text())
            self.target_position["z"] = float(self.z_target.text())
            
            self.target_orientation["roll"] = float(self.roll_target.text())
            self.target_orientation["pitch"] = float(self.pitch_target.text())
            self.target_orientation["yaw"] = float(self.yaw_target.text())
            
            # If roboticstoolbox is not available, use analytical inverse kinematics
            if not ROBOTICS_TOOLBOX_AVAILABLE or self.robot is None:
                solutions = self.analytical_inverse_kinematics()
            else:
                # Use roboticstoolbox for inverse kinematics
                solutions = self.robotics_toolbox_inverse_kinematics()
            
            # Save solutions for later use
            self.ik_solutions = solutions
            
            # Display solutions
            if solutions:
                solutions_text = ""
                for i, solution in enumerate(solutions):
                    solutions_text += f"Solution {i + 1}: {[round(val, 2) for val in solution]}\n"
                self.solutions_display.setText(solutions_text)
                
                print(f"Inverse kinematics calculated for target: "
                      f"pos=({self.target_position['x']}, {self.target_position['y']}, {self.target_position['z']}), "
                      f"orient=({self.target_orientation['roll']}, {self.target_orientation['pitch']}, {self.target_orientation['yaw']})")
            else:
                self.solutions_display.setText("No valid solutions found.")
        except Exception as e:
            self.solutions_display.setText(f"Error calculating inverse kinematics: {str(e)}")
            print(f"Error in inverse kinematics: {e}")
    
    def robotics_toolbox_inverse_kinematics(self):
        """Use roboticstoolbox to calculate inverse kinematics solutions."""
        if not ROBOTICS_TOOLBOX_AVAILABLE:
            return []
        
        try:
            # Create the target pose
            position = [self.target_position["x"], self.target_position["y"], self.target_position["z"]]
            
            # Convert orientation to radians if in degrees
            if self.angle_unit == "deg":
                orientation = [
                    np.radians(self.target_orientation["roll"]),
                    np.radians(self.target_orientation["pitch"]),
                    np.radians(self.target_orientation["yaw"])
                ]
            else:
                orientation = [
                    self.target_orientation["roll"],
                    self.target_orientation["pitch"],
                    self.target_orientation["yaw"]
                ]
            
            sol = compute_inverse_kinematics(self.robot, position, orientation)

            q_sol = sol.q
                
            # Convert to degrees if needed
            if self.angle_unit == "deg":
                q_sol = np.round(np.rad2deg(q_sol), 2)
            
            # Return solutions
            print("IK solutions:", q_sol)
            return [q_sol]
            #else:
            #    print("IK did not converge")
            #    return []
        except Exception as e:
            print(f"Error in roboticstoolbox IK: {e}")
            return []
    
    
    
    def apply_ik_solution(self):
        """Apply the first IK solution to the robot joints."""
        if hasattr(self, 'ik_solutions') and self.ik_solutions and self.set_joints_callback:
            try:
                # Use the first solution by default
                solution = self.ik_solutions[0]
                
                # Call the callback to set the joint values in the main app
                self.set_joints_callback(solution)
                
                self.solutions_display.setText(f"Applied solution: {[round(val, 2) for val in solution]}")
                print(f"Applied IK solution: {solution}")
            except Exception as e:
                self.solutions_display.setText(f"Error applying solution: {str(e)}")
                print(f"Error applying IK solution: {e}")
        else:
            self.solutions_display.setText("No solutions available to apply.") 