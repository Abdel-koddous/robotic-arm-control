from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QPushButton, QLabel
from PyQt6.QtCore import Qt
from serial_interface_control import SerialInterface
class RoboticArmControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.serial_interface = SerialInterface(port='COM5', baudrate=9600)
        self.serial_interface.connect()

    def init_ui(self):
        
        self.setWindowTitle("Robotic Arm Control")
        self.setGeometry(100, 100, 300, 200)

        layout = QHBoxLayout()
        
        self.label = QLabel("Shoulder Joint: 0")
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(100)
        self.slider.setRange(0, 5000)
        self.slider.setValue(0)
        layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self.update_label)

        self.button = QPushButton("Send Command")
        self.button.clicked.connect(self.send_command)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"Shoulder Joint: {value}")

    def send_command(self):
        value = self.slider.value()
        command = f"m10{value}"  # Example command format
        print(f"Sending command: {command}")
        # Here you would call the method to send the command to the serial interface
        self.serial_interface.send_move_joint_command(command)

    def clean_up(self):
        self.serial_interface.close()

if __name__ == "__main__":
    app = QApplication([])
    window = RoboticArmControlApp()
    window.show()
    app.exec()
