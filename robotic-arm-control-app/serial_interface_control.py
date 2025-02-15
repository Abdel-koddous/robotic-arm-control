import serial
import time

class SerialInterface:
    def __init__(self, port='COM5', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None

    def set_port(self, port):
        self.port = port

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    def connect(self):
        success = False
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate)
            print(f"Connected to {self.port} at {self.baudrate} baud.")
            time.sleep(0.5) # wait for the connection to be established
            success = True
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")
        return success

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

