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

    def monitor_move_joint_command(self, timeout=5):
        """
        Monitor the move joint command until the stepper STARTED message.
        timeout is in seconds.
        """
        start_time = time.time()
        serial_output = "none"
        print("Monitoring move joint command...")
        if self.serial_connection and self.serial_connection.is_open:
            while self.serial_connection.in_waiting > 0:
                serial_output = self.serial_connection.readline().decode('utf-8').rstrip()
                print(serial_output)
                if "STARTED moving..." in serial_output:
                    break
                if time.time() - start_time > timeout:
                    print("Timeout: move joint command not received")
                    break
                time.sleep(0.05)
        else:
            print("Serial connection is not open.")

        return serial_output

    def send_move_joint_command(self, command):
        success = True

        self.send_command(command)
        time.sleep(0.5)
        # number_of_motors = command.count("m")
        # motors_started = 0
        # for i in range(number_of_motors):
        #    result = self.monitor_move_joint_command(timeout=10)    
        #   if "STARTED moving..." in result:
        #         motors_started += 1
        #    
        #     if motors_started == number_of_motors:
        #             success = True
        #             break
        #        
        return success

if __name__ == "__main__":

    serial_interface = SerialInterface(port='COM6', baudrate=9600)

    serial_interface.connect()
    # Example command to send to the Arduino
    move_joint_command = "m002005m101000m201500"      
    serial_interface.send_move_joint_command(move_joint_command)

    # time.sleep(10)
    # move_joint_command = "m000" 
    # serial_interface.send_move_joint_command(move_joint_command)

    serial_interface.close()

