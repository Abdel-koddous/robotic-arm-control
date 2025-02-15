import serial
import time

class SerialInterface:
    def __init__(self, port='COM5', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None

    def connect(self):
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate)
            print(f"Connected to {self.port} at {self.baudrate} baud.")
            time.sleep(2)
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")

    def send_command(self, command):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(command.encode())
            print(f"Sent command: {command}")
        else:
            print("Serial connection is not open.")

    def close(self):
        if self.serial_connection:
            self.serial_connection.close()
            print("Serial connection closed.")

    def read_output(self):
        output = "none"
        if self.serial_connection and self.serial_connection.is_open:
            while self.serial_connection.in_waiting > 0:
                output = self.serial_connection.readline().decode('utf-8').rstrip()
                print(output)
                # Loop until the stepper STARTED message is received
                if "STARTED moving..." in output:
                    break
                time.sleep(0.1)
        return output

    def send_move_joint_command(self, command):
        success = False

        self.send_command(command)
        while True:
            output = self.read_output()
            if "STARTED moving..." in output:
                print("Congrats! move joint command sent successfully :)")
                success = True
                break
            time.sleep(1)
        return success

    def create_connection_control(self):
        """Create the connection control panel"""
        connection_layout = QHBoxLayout()
        
        # Port input
        port_label = QLabel("COM Port:")
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
        if self.serial_connection and self.serial_connection.is_open:
            self.close()
            self.connect_button.setText("Connect")
            self.connection_status.setText("Not Connected")
            self.connection_status.setStyleSheet("color: red;")
            self.port_input.setEnabled(True)
        else:
            try:
                port = self.port_input.text()
                self.connect(port, baudrate=9600)
                self.connect_button.setText("Disconnect")
                self.connection_status.setText("Connected")
                self.connection_status.setStyleSheet("color: green;")
                self.port_input.setEnabled(False)
            except Exception as e:
                self.connection_status.setText(f"Error: {str(e)}")
                self.connection_status.setStyleSheet("color: red;")

    def is_connected(self):
        return self.serial_connection is not None and self.serial_connection.is_open

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Connection Group
        connection_group = QGroupBox("Connection")
        connection_group.setStyleSheet("""
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
        connection_group.setLayout(self.create_connection_control())
        main_layout.addWidget(connection_group)
        
        # Rest of your existing groups...
        # Joint Controls Group
        joints_group = QGroupBox("Joint Controls")
        # ... rest of the existing code ...

if __name__ == "__main__":

    serial_interface = SerialInterface(port='COM6', baudrate=9600)

    serial_interface.connect()
    # Example command to send to the Arduino
    move_joint_command = "m002000m101000m201500"      
    serial_interface.send_move_joint_command(move_joint_command)

    time.sleep(10)
    move_joint_command = "m000" 
    serial_interface.send_move_joint_command(move_joint_command)

    serial_interface.close()

