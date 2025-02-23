from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QPushButton, QLabel, QVBoxLayout, QLineEdit, QListWidget, QGroupBox, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from serial_interface_control import SerialInterface
from sequence_manager import SequenceManager
import threading

class RoboticArmControlApp(QWidget):
    """
    Main application class for the robotic arm control GUI.
    """
    def __init__(self):
        super().__init__()
        self.serial_interface = SerialInterface()
        self.joint_values = [0, 0, 0, 0, 0]  # Updated for 5 joints
        self.sequence_manager = SequenceManager(self.serial_interface)
        self.sequence_manager.current_pose_changed.connect(self.update_current_pose_label)      
        self.sequence_thread = None
        self.joint_status_labels = {}
        # Create and start status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_all_joint_status)
        self.status_timer.start(100)  # Update every 100ms

        self.init_ui()

    def update_current_pose_label(self, current_pose_index, total_poses):
        """
        Update the current pose label with the current pose index 
        in the running sequence out of total poses.
        """
        self.current_pose_label.setText(
            f"{current_pose_index + 1} / {total_poses}"
        )

    def create_joint_control(self, joint_name, joint_id, initial_value):
        """
        Create a control panel for a single joint.
        """
        joint_layout = QHBoxLayout()  
        
        label = QLabel(f"{joint_name} Joint: {initial_value}")
        label.setMinimumWidth(120)  # Set minimum width for the joint control text
        joint_layout.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(110)
        slider.setRange(-7000, 7000)
        slider.setValue(0)
        slider.setMinimumWidth(200)
        joint_layout.addWidget(slider)

        value_input = QLineEdit()
        value_input.setText(str(initial_value))  
        value_input.setFixedWidth(100)
        joint_layout.addWidget(value_input)  

        button = QPushButton("Set")
        button.clicked.connect(lambda: self.send_command(joint_id, slider.value()))
        button.setMinimumWidth(100)
        joint_layout.addWidget(button)  

        # Add status indicator
        self.joint_status_labels[joint_id] = QFrame()
        self.joint_status_labels[joint_id].setFixedSize(15, 15)  # Set size of the LED
        self.joint_status_labels[joint_id].setStyleSheet("background-color: gray;")  # Default color (off)
        joint_layout.addWidget(self.joint_status_labels[joint_id])
        
        slider.valueChanged.connect(lambda value: self.update_label(label, joint_name, value))
        slider.valueChanged.connect(lambda value: value_input.setText(str(value)))  
        slider.valueChanged.connect(lambda value: self.set_joint_value(joint_id, value))
        value_input.textChanged.connect(lambda text: slider.setValue(int(text)) if text.lstrip('-').isdigit() else slider.setValue(0))
        value_input.textChanged.connect(lambda text: self.set_joint_value(joint_id, int(text)) if text.lstrip('-').isdigit() else self.set_joint_value(joint_id, 0))
        
        return joint_layout  
    
    def set_joint_value(self, joint_id, value):
        """
        Set the value of a joint in joint_values list attribute.
        """
        self.joint_values[joint_id] = value
    
    def get_joint_value(self, joint_id):
        """
        Get the value of a joint from the joint_values list attribute.
        """
        return self.joint_values[joint_id]
    
    def create_gripper_control(self):
        """
        Create a control panel for the gripper.
        """
        gripper_layout = QHBoxLayout()

        open_button = QPushButton("Open Gripper (Disabled for now)")
        open_button.clicked.connect(lambda: self.send_command(6, 0))
        gripper_layout.addWidget(open_button)

        close_button = QPushButton("Close Gripper (Disabled for now)")
        close_button.clicked.connect(lambda: self.send_command(6, 1))
        gripper_layout.addWidget(close_button)

        return gripper_layout

    def create_set_all_joints_control(self):
        control_all_joints_layout = QVBoxLayout()
        
        button = QPushButton("SET All Joints")
        button.clicked.connect(lambda: self.send_move_all_joints_command())
        button.setMinimumWidth(100)
        control_all_joints_layout.addWidget(button)

        # Add Home All Joints button
        home_button = QPushButton("HOME All Joints")
        home_button.clicked.connect(self.home_all_joints)
        home_button.setMinimumWidth(100)
        control_all_joints_layout.addWidget(home_button)
        
        stop_button = QPushButton("STOP All Steppers")
        stop_button.clicked.connect(lambda: self.serial_interface.send_command("s"))
        stop_button.setMinimumWidth(100)
        control_all_joints_layout.addWidget(stop_button)

        return control_all_joints_layout

    def home_all_joints(self):
        """Reset all joints to home position (0)"""
        # First, reset all joint values in memory
        for joint_id in range(len(self.joint_values)):
            self.joint_values[joint_id] = 0
        
        # Get the joints group from main layout
        main_layout = self.layout()
        joints_group = None
        
        # Find the joints group
        for i in range(main_layout.count()):
            widget = main_layout.itemAt(i).widget()
            if isinstance(widget, QGroupBox) and widget.title() == "Joint Controls":
                joints_group = widget
                break
        
        if joints_group:
            joints_layout = joints_group.layout()
            # Update each joint's controls
            for joint_id in range(joints_layout.count()):
                joint_layout = joints_layout.itemAt(joint_id)
                if joint_layout:
                    # Update each widget in the joint layout
                    for i in range(joint_layout.count()):
                        widget = joint_layout.itemAt(i).widget()
                        if isinstance(widget, QLabel):
                            # Update label
                            joint_name = ["Base", "Shoulder", "Elbow", "Wrist", "Hand"][joint_id]
                            widget.setText(f"{joint_name} Joint: 0")
                        elif isinstance(widget, QSlider):
                            # Update slider
                            widget.setValue(0)
                        elif isinstance(widget, QLineEdit):
                            # Update input field
                            widget.setText("0")
        
        # Send command to move all joints to 0
        self.send_move_all_joints_command()
        print("All joints homed to 0 position")
    
    def create_sequence_control(self):
        """Create the sequence control panel"""
        sequence_layout = QVBoxLayout()

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
        interval_layout.addWidget(QLabel("Interval Between Poses (seconds):"))
        
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
    
           # Status label
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Sequence Status"))
        self.sequence_status_label = QLabel("Idle")
        self.sequence_status_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.sequence_status_label)

        status_layout.addWidget(QLabel("Current Pose"))
        self.current_pose_label = QLabel(f"0 / {len(self.sequence_manager.poses)}")
        self.current_pose_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.current_pose_label)


        sequence_layout.addLayout(status_layout)
        

        return sequence_layout

    def create_connection_control(self):
        """Create the connection control panel"""
        connection_layout = QHBoxLayout()
        
        # Port input
        port_label = QLabel("Arduino COM Port")
        self.port_input = QLineEdit()
        self.port_input.setText("COM6")  # Default port
        self.port_input.setFixedWidth(100)
        
        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        
        # Status label
        self.connection_status = QLabel("Not Connected")
        self.connection_status.setStyleSheet("color: red;")
        
        connection_layout.addWidget(port_label)
        connection_layout.addWidget(self.port_input)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(self.connection_status)
        
        return connection_layout

    def toggle_connection(self):

        if self.serial_interface.serial_connection and self.serial_interface.serial_connection.is_open:
            self.serial_interface.close()
            self.connect_button.setText("Connect")
            self.connection_status.setText("Not Connected")
            self.connection_status.setStyleSheet("color: red;")
            self.port_input.setEnabled(True)

            for joint_id in range(len(self.serial_interface.joints_status)):
                self.serial_interface.set_joint_status(joint_id, "idle")

        else:
            port = self.port_input.text()
            self.serial_interface.set_port(port)
            success = self.serial_interface.connect()
            if success:
                self.connect_button.setText("Disconnect")
                self.connection_status.setText("Connected")
                self.connection_status.setStyleSheet("color: green;")
                self.port_input.setEnabled(False)
            else:
                self.connection_status.setText("Failed to connect")
                self.connection_status.setStyleSheet("color: red;")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # Increase spacing between sections
    
        # Connection Control Group
        connection_group = QGroupBox("Connection Control")
        connection_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: white;
            }
        """)
        connection_layout = QVBoxLayout()
        connection_layout.addLayout(self.create_connection_control())
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)

        # Joint Controls Group
        joints_group = QGroupBox("Joint Controls")
        joints_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        joints_layout = QVBoxLayout()
        joints_layout.addLayout(self.create_joint_control("Base", 0, 0))
        joints_layout.addLayout(self.create_joint_control("Shoulder", 1, 0))
        joints_layout.addLayout(self.create_joint_control("Elbow", 2, 0))
        joints_layout.addLayout(self.create_joint_control("Wrist", 3, 0))
        joints_layout.addLayout(self.create_joint_control("Hand", 4, 0))
        joints_group.setLayout(joints_layout)
        main_layout.addWidget(joints_group)

        # Global Controls Group
        global_controls_group = QGroupBox("Global Controls")
        global_controls_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: white;
            }
        """)
        global_layout = QVBoxLayout()
        global_layout.addLayout(self.create_set_all_joints_control())
        global_layout.addLayout(self.create_gripper_control())
        global_controls_group.setLayout(global_layout)
        main_layout.addWidget(global_controls_group)

        # Sequence Control Group
        sequence_group = QGroupBox("Sequence Control")
        sequence_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: white;
            }
        """)
        sequence_layout = QVBoxLayout()
        sequence_layout.addLayout(self.create_sequence_control())
        sequence_group.setLayout(sequence_layout)
        main_layout.addWidget(sequence_group)

        # Add some padding around the entire window
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

    def update_label(self, label, joint_name, value):
        label.setText(f"{joint_name} Joint: {value}")

    def send_command(self, joint_id, value):
        # Determine if value is negative and create appropriate command
        direction = "1" if value < 0 else "0"
        abs_value = abs(value)
        command = f"m{joint_id}{direction}{abs_value}"
        
        if joint_id == 6:
            self.serial_interface.send_command(command)
        else:
            self.serial_interface.send_move_joint_command(command)

    def send_move_all_joints_command(self):
        """Send command to move all joints to their respective target positions."""
        move_all_joints_command = ""
        for i, joint_value in enumerate(self.joint_values):
            direction = "0" if joint_value >= 0 else "1"
            abs_value = abs(joint_value)
            move_all_joints_command += f"m{i}{direction}{abs_value}"

        self.serial_interface.send_move_joint_command(move_all_joints_command)

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
        
        self.sequence_status_label.setText("Running...")
        self.sequence_status_label.setStyleSheet("color: #00FF00;")  # Green color
        
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
        
        self.sequence_status_label.setText("Stopped")
        self.sequence_status_label.setStyleSheet("color: red;")

    def clean_up(self):
        self.stop_sequence()
        self.serial_interface.close()

    def clear_sequence(self):
        """Clear the sequence and update the display"""
        self.sequence_manager.clear_sequence()
        self.update_poses_list()  # Update the UI list after clearing
        self.sequence_status_label.setText("Idle")
        self.sequence_status_label.setStyleSheet("color: gray;")

    def update_all_joint_status(self):
        """Update all joint status indicators based on SerialInterface status"""
        if hasattr(self.serial_interface, 'joints_status') and self.serial_interface.joints_status:
            for joint_id in range(len(self.serial_interface.joints_status)):
                status = self.serial_interface.joints_status[joint_id]
                self.update_joint_status_indicator(joint_id, status)

    def update_joint_status_indicator(self, joint_id, status):
        """Update the visual indicator for a specific joint"""
        if joint_id in self.joint_status_labels:
            status_colors = {
                'idle': '#808080',      # Gray
                'running': '#FFA500',     # Orange
                'done': '#00FF00',  # Green
                'unknown': '#FFFF00'        # Yellow
            }
            color = status_colors.get(status, '#808080')
            self.joint_status_labels[joint_id].setStyleSheet(
                f"background-color: {color}; border-radius: 7px;"
            )

if __name__ == "__main__":
    
    app = QApplication([])

    app.setApplicationName("MOGA Robotics | 5DOF Arm Control")  # Set the application name
    app.setWindowIcon(QIcon("data/app_logo.png")) # set the logo for the application
    app.setStyleSheet("""
        QWidget {
            background-color: #222222; 
            color: #FFFFFF;
        }
    """)

    window = RoboticArmControlApp()
    window.show()
    app.exec()

