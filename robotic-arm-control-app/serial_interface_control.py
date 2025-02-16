import serial
import time
import threading

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
            #print(f"Sent command: {command}")
        else:
            print("Serial connection is not open.")

    def close(self):
        if self.serial_connection:
            self.serial_connection.close()
            print("Serial connection closed.")

    def monitor_move_joint_command(self, current_status, timeout=10):
        """
        Monitor the move joint command until the move joint command is received.
        timeout is in seconds.
        """
        start_time = time.time()
        serial_output = "none"
        new_joint_status = current_status
        print("Monitoring move joint command...")
        if self.serial_connection and self.serial_connection.is_open:
            while True:
                if (time.time() - start_time) > timeout:
                    print("ERROR: Timeout - MOVE JOINT DID NOT GO THROUGH...")
                    break
                elif self.serial_connection.in_waiting > 0:
                    serial_output = self.serial_connection.readline().decode('utf-8').rstrip()
                    #print(serial_output)
                    if "run" in serial_output:
                        new_joint_status = "running"
                        print(f"Joint status: {new_joint_status}")
                    elif "done" in serial_output:
                        new_joint_status = "done"
                        print(f"Joint status: {new_joint_status}")
                        break

                time.sleep(0.05) # 50 ms
        else:
            print("Serial connection is not open.")

        return new_joint_status

    def send_move_joint_command(self, command):
        """
        Send the move joint command to the Arduino & monitor the joint status 
        until the move joint command is started.
        """
        joint_status = "idle"
        print("--------------------------------")
        print(f"Sending Move Joint Command: {command}")
        self.send_command(command)

        # Create a thread to monitor the move joint command
        monitor_thread = threading.Thread(
            target=self.monitor_move_joint_command,
            kwargs={'current_status': joint_status, 'timeout': 10}
        )
        # Start the monitoring thread
        monitor_thread.start()

        # return some feedback?


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

