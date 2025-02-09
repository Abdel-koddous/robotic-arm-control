from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QPushButton, QLabel, QVBoxLayout, QLineEdit, QFormLayout, QListWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from serial_interface_control import SerialInterface
from sequence_manager import SequenceManager
import threading

class RoboticArmControlApp(QWidget):
    def __init__(self, port='COM5'):
        super().__init__()
        self.serial_interface = SerialInterface(port, baudrate=9600)
        self.serial_interface.connect()
        self.joint_values = [0, 0, 0, 0, 0]  # Updated for 5 joints
        self.sequence_manager = SequenceManager(self.serial_interface)
        self.sequence_thread = None
        self.init_ui()

    def create_joint_control(self, joint_name, joint_id, initial_value):
        joint_layout = QHBoxLayout()  
        
        label = QLabel(f"{joint_name} Joint: {initial_value}")
        label.setMinimumWidth(100)
        joint_layout.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(100)
        slider.setRange(0, 10000)
        slider.setValue(initial_value)
        slider.setMinimumWidth(200)
        joint_layout.addWidget(slider)

        value_input = QLineEdit()
        value_input.setText(str(initial_value))  
        value_input.setFixedWidth(100)
        joint_layout.addWidget(value_input)  

        button = QPushButton("Set Joint")
        button.clicked.connect(lambda: self.send_command(joint_id, slider.value()))
        button.setMinimumWidth(100)
        joint_layout.addWidget(button)  

        slider.valueChanged.connect(lambda value: self.update_label(label, joint_name, value))
        slider.valueChanged.connect(lambda value: value_input.setText(str(value)))  
        slider.valueChanged.connect(lambda value: self.set_joint_value(joint_id, value))
        value_input.textChanged.connect(lambda text: slider.setValue(int(text)) if text.isdigit() else None)  
        value_input.textChanged.connect(lambda text: self.set_joint_value(joint_id, int(text)))

        return joint_layout  
    
    def set_joint_value(self, joint_id, value):
        self.joint_values[joint_id] = value
    
    def get_joint_value(self, joint_id):
        return self.joint_values[joint_id]
    
    def create_gripper_control(self):
        gripper_layout = QHBoxLayout()

        open_button = QPushButton("Open Gripper (Broken for now)")
        open_button.clicked.connect(lambda: self.send_command(3, 0))
        gripper_layout.addWidget(open_button)

        close_button = QPushButton("Close Gripper (Broken for now)")
        close_button.clicked.connect(lambda: self.send_command(3, 1))
        gripper_layout.addWidget(close_button)

        return gripper_layout

    def create_set_all_joints_control(self):
        control_all_joints_layout = QVBoxLayout()
        
        button = QPushButton("SET All Joints")
        button.clicked.connect(lambda: self.send_move_all_joints_command())
        button.setMinimumWidth(100)
        control_all_joints_layout.addWidget(button)
        
        stop_button = QPushButton("STOP All Steppers")
        stop_button.clicked.connect(lambda: self.serial_interface.send_command("s"))
        stop_button.setMinimumWidth(100)
        control_all_joints_layout.addWidget(stop_button)

        return control_all_joints_layout
    
    def create_sequence_control(self):
        """Create the sequence control panel"""
        sequence_layout = QVBoxLayout()
        
        # Title for the section
        title = QLabel("Sequence Control")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        sequence_layout.addWidget(title)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add current pose button
        add_pose_button = QPushButton("Add Current Pose")
        add_pose_button.clicked.connect(self.add_current_pose)
        buttons_layout.addWidget(add_pose_button)
        
        # Play sequence button
        play_button = QPushButton("Play Sequence")
        play_button.clicked.connect(self.play_sequence)
        buttons_layout.addWidget(play_button)
        
        # Stop sequence button
        stop_button = QPushButton("Stop Sequence")
        stop_button.clicked.connect(self.stop_sequence)
        buttons_layout.addWidget(stop_button)
        
        # Clear sequence button
        clear_button = QPushButton("Clear Sequence")
        clear_button.clicked.connect(self.clear_sequence)
        buttons_layout.addWidget(clear_button)
        
        sequence_layout.addLayout(buttons_layout)
        
        # Interval control
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Interval (seconds):"))
        
        self.interval_input = QLineEdit()
        self.interval_input.setText(str(self.sequence_manager.interval))
        self.interval_input.setFixedWidth(100)
        self.interval_input.textChanged.connect(
            lambda text: self.sequence_manager.set_interval(float(text)) if text and text.replace('.', '').isdigit() else None
        )
        interval_layout.addWidget(self.interval_input)
        
        sequence_layout.addLayout(interval_layout)
        
        # List of saved poses
        sequence_layout.addWidget(QLabel("Saved Poses:"))
        self.poses_list = QListWidget()
        self.poses_list.setMinimumHeight(100)
        sequence_layout.addWidget(self.poses_list)
        
        return sequence_layout

    def init_ui(self):
        main_layout = QVBoxLayout()  
        self.setWindowTitle("Robotic Arm Control Interface")
        self.setWindowIcon(QIcon("data/app_logo.png"))

        # Create joint controls for all 5 joints
        main_layout.addLayout(self.create_joint_control("Base", 0, 0))
        main_layout.addLayout(self.create_joint_control("Shoulder", 1, 0))
        main_layout.addLayout(self.create_joint_control("Elbow", 2, 0))
        main_layout.addLayout(self.create_joint_control("Wrist", 3, 0))
        main_layout.addLayout(self.create_joint_control("Hand", 4, 0))

        main_layout.addLayout(self.create_set_all_joints_control())
        main_layout.addLayout(self.create_gripper_control())
        
        # Add sequence control section
        main_layout.addLayout(self.create_sequence_control())

        self.setLayout(main_layout)

    def update_label(self, label, joint_name, value):
        label.setText(f"{joint_name} Joint: {value}")

    def send_command(self, joint_id, value):
        command = f"m{joint_id}0{value}"
        print(f"Sending command: {command}")
        if joint_id == 3:
            self.serial_interface.send_command(command)
        else:
            self.serial_interface.send_move_joint_command(command)
    
    def send_move_all_joints_command(self):
        command = f"m00{self.joint_values[0]}m10{self.joint_values[1]}m20{self.joint_values[2]}m30{self.joint_values[3]}m40{self.joint_values[4]}"
        self.serial_interface.send_move_joint_command(command)

    def add_current_pose(self):
        """Add current joint values as a pose to the sequence"""
        pose_index = self.sequence_manager.add_pose(self.joint_values)
        self.update_poses_list()
        print(f"Added pose {pose_index} with values: {self.joint_values}")

    def update_poses_list(self):
        """Update the list of poses in the UI"""
        self.poses_list.clear()
        for i, pose in enumerate(self.sequence_manager.poses):
            self.poses_list.addItem(f"Pose {i + 1}: {pose.joint_values}")

    def play_sequence(self):
        """Start playing the sequence in a separate thread"""
        if self.sequence_thread and self.sequence_thread.is_alive():
            print("Sequence is already playing")
            return
        
        self.sequence_thread = threading.Thread(
            target=self.sequence_manager.play_sequence,
            kwargs={'back_and_forth': True}
        )
        self.sequence_thread.start()
    
    def stop_sequence(self):
        """Stop the sequence playback"""
        self.sequence_manager.stop_sequence()
        if self.sequence_thread:
            self.sequence_thread.join()
    
    def clean_up(self):
        self.stop_sequence()
        self.serial_interface.close()

    def clear_sequence(self):
        """Clear the sequence and update the display"""
        self.sequence_manager.clear_sequence()
        self.update_poses_list()  # Update the UI list after clearing

if __name__ == "__main__":
    app = QApplication([])
    window = RoboticArmControlApp(port='COM6')
    window.show()
    app.exec()

