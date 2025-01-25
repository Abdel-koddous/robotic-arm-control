from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QPushButton, QLabel, QVBoxLayout, QLineEdit, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from serial_interface_control import SerialInterface
class RoboticArmControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.serial_interface = SerialInterface(port='COM6', baudrate=9600)
        self.serial_interface.connect()
        self.joint_values = [0, 0, 0]

    def create_joint_control(self, joint_name, joint_id, initial_value):
        # Create a horizontal layout for the joint control
        joint_layout = QHBoxLayout()  
        
        # Create and add the label
        label = QLabel(f"{joint_name} Joint: {initial_value}")
        label.setMinimumWidth(100)  # Set minimum width for the label
        joint_layout.addWidget(label)

        # Create and add the slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(100)
        slider.setRange(0, 10000)
        slider.setValue(initial_value)
        slider.setMinimumWidth(200)  # Set minimum width for the slider
        joint_layout.addWidget(slider)

        # Create and add the input field
        value_input = QLineEdit()  
        value_input.setText(str(initial_value))  
        value_input.setFixedWidth(100) # Set fixed width for the input field
        joint_layout.addWidget(value_input)  

        # Create and add the button
        button = QPushButton("Set Joint")
        button.clicked.connect(lambda: self.send_command(joint_id, slider.value()))
        button.setMinimumWidth(100)  # Set minimum width for the button
        joint_layout.addWidget(button)  

        slider.valueChanged.connect(lambda value: self.update_label(label, joint_name, value))
        slider.valueChanged.connect(lambda value: value_input.setText(str(value)))  
        slider.valueChanged.connect(lambda value: self.set_joint_value(joint_id, value))
        value_input.textChanged.connect(lambda text: slider.setValue(int(text)) if text.isdigit() else None)  
        value_input.textChanged.connect(lambda text: self.set_joint_value(joint_id, int(text)))

        return joint_layout  # Return the horizontal layout for the joint control
    
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
        button.setMinimumWidth(100)  # Set minimum width for the button
        control_all_joints_layout.addWidget(button)
        
        stop_button = QPushButton("STOP All Steppers")
        stop_button.clicked.connect(lambda: self.serial_interface.send_command("s"))
        stop_button.setMinimumWidth(100)  # Set minimum width for the button
        control_all_joints_layout.addWidget(stop_button)

        return control_all_joints_layout
    
    def init_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout()  

        # Set the window title
        self.setWindowTitle("Robotic Arm Control Interface")
        
        # Set the window icon
        self.setWindowIcon(QIcon("data/app_logo.png"))

        # Create joint controls
        main_layout.addLayout(self.create_joint_control("Base", 0, 0))
        main_layout.addLayout(self.create_joint_control("Shoulder", 1, 0))
        main_layout.addLayout(self.create_joint_control("Elbow", 2, 0))

        main_layout.addLayout(self.create_set_all_joints_control())

        main_layout.addLayout(self.create_gripper_control())



        self.setLayout(main_layout)  # Set the main layout

    def update_label(self, label, joint_name, value):
        label.setText(f"{joint_name} Joint: {value}")

    def send_command(self, joint_id, value):
        command = f"m{joint_id}0{value}"  # Command format for motor steps
        print(f"Sending command: {command}")
        if joint_id == 3:  # Gripper servo specific mgt
            self.serial_interface.send_command(command)
        else:
            self.serial_interface.send_move_joint_command(command)
    
    def send_move_all_joints_command(self):
        command = f"m00{self.joint_values[0]}m10{self.joint_values[1]}m20{self.joint_values[2]}"
        self.serial_interface.send_move_joint_command(command)


    def clean_up(self):
        self.serial_interface.close()

if __name__ == "__main__":
    app = QApplication([])
    window = RoboticArmControlApp()
    window.show()
    app.exec()
