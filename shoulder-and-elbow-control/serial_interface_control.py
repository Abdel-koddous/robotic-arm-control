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
            time.sleep(1)
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
                # Loop until the stepper STARTED message is received
                if "stepper STARTED" in output:
                    break
                time.sleep(0.1)
        return output

if __name__ == "__main__":
    serial_interface = SerialInterface(port='COM5', baudrate=9600)
    serial_interface.connect()
    
    time.sleep(1)
    # Example command to send to the Arduino
    move_joint_command = "m10100"  
    serial_interface.send_command(move_joint_command)

    while True:
        output = serial_interface.read_output()
        if "stepper STARTED" in output:
            print("Congrats! move joint command sent successfully :)")
            break
        time.sleep(1)

    serial_interface.close()
