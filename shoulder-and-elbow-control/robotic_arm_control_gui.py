from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from serial_interface_control import SerialInterface
class RoboticArmControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.serial_interface = SerialInterface(port='COM5', baudrate=9600)
        self.serial_interface.connect()

    def create_joint_control(self, joint_name, joint_id, initial_value):
        layout = QHBoxLayout()
        label = QLabel(f"{joint_name} Joint: {initial_value}")
        layout.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(100)
        slider.setRange(0, 10000)
        slider.setValue(initial_value)
        layout.addWidget(slider)

        slider.valueChanged.connect(lambda value: self.update_label(label, joint_name, value))

        button = QPushButton("Set Joint")
        button.clicked.connect(lambda: self.send_command(joint_id, slider.value()))
        layout.addWidget(button)

        return layout
    
    def create_gripper_control(self):
        gripper_layout = QHBoxLayout()

        open_button = QPushButton("Open Gripper")
        open_button.clicked.connect(lambda: self.send_command(3, 0))
        gripper_layout.addWidget(open_button)

        close_button = QPushButton("Close Gripper")
        close_button.clicked.connect(lambda: self.send_command(3, 1))
        gripper_layout.addWidget(close_button)

        return gripper_layout

    def init_ui(self):
        main_layout = QVBoxLayout()  # Main vertical layout

        # Create joint controls
        main_layout.addLayout(self.create_joint_control("Base", 0, 0))
        main_layout.addLayout(self.create_joint_control("Shoulder", 1, 0))
        main_layout.addLayout(self.create_joint_control("Elbow", 2, 0))
        main_layout.addLayout(self.create_gripper_control())

        self.setLayout(main_layout)  # Set the main layout

    def update_label(self, label, joint_name, value):
        label.setText(f"{joint_name} Joint: {value}")

    def send_command(self, joint_id, value):
        command = f"m{joint_id}0{value}"  # Example command format
        print(f"Sending command: {command}")
        if joint_id == 3: # Gripper servo specific mgt
            self.serial_interface.send_command(command)
        else:
            self.serial_interface.send_move_joint_command(command)

    def clean_up(self):
        self.serial_interface.close()

if __name__ == "__main__":
    app = QApplication([])
    window = RoboticArmControlApp()
    window.show()
    app.exec()
