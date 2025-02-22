import serial
import time
import threading

class SerialInterface:
    def __init__(self, port='COM5', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.num_joints = 5
        self.joints_status = ["idle"] * self.num_joints
        self.move_command_monitoring_done = False

    def set_port(self, port):
        self.port = port

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    def get_move_command_monitoring_done(self):
        """Return the status of move joint command monitoring."""
        return self.move_command_monitoring_done

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

    def monitor_move_joint_command(self, command_to_monitor, timeout=60):
        """
        Monitor the move joint command until the move joint command is received.
        timeout is in seconds.
        """
        print(f"SerialInterface Class - Monitoring move joint command: {command_to_monitor}")
        self.move_command_monitoring_done = False
        start_time = time.time()
        serial_connection_monitoring_period = 0.1 # 100 ms
        no_data_received_message_period = 3 # seconds
        serial_connection_waiting_count = 0

        if self.serial_connection and self.serial_connection.is_open:
            while True:
                if (time.time() - start_time) > timeout:
                    print(f"ERROR: Timeout - MOVE JOINT COMMAND {command_to_monitor} DID NOT GO THROUGH...")
                    self.move_command_monitoring_done = False
                    break
                
                if self.serial_connection.in_waiting > 0:
                    serial_output = self.serial_connection.readline().decode('utf-8').rstrip()
                    print(f"serial_output => {serial_output}")
                    if "run" in serial_output or "done" in serial_output:
                        self.update_joint_status(serial_output)
                        print(f"Joints status: {self.joints_status}")
                    if "done" in serial_output and "running" not in self.joints_status:
                        print("#### All joints movements are COMPLETED... Monitoring is over.")
                        self.serial_connection.reset_input_buffer()  # Flush the input buffer of serial connection
                        self.move_command_monitoring_done = True
                        break
                    
                    serial_connection_waiting_count = 0

                else:
                    serial_connection_waiting_count += 1
                    if serial_connection_waiting_count > (
                        no_data_received_message_period / serial_connection_monitoring_period
                    ):
                        print(f"Monitoring - No data received from the serial connection in the last "
                              f"{no_data_received_message_period} seconds...")
                        serial_connection_waiting_count = 0
                               
                time.sleep(serial_connection_monitoring_period) # 100 ms
        else:
            print("Serial connection is not open.")



    def send_move_joint_command(self, command):
        """
        Send the move joint command to the Arduino & monitor the joint status 
        until the move joint command is started.
        """
        print("########################################################")
        print(f"SerialInterface Class - Sending Move Joint Command: {command}")
        self.send_command(command)

        # Create a thread to monitor the move joint command
        monitor_thread = threading.Thread(
            target=self.monitor_move_joint_command,
            kwargs={'command_to_monitor': command, 'timeout': 45}
        )
        # Start the monitoring thread
        monitor_thread.start()

        # return some feedback?

    def update_joint_status(self, serial_output):
        """
        Update the joint status from the serial output 
        example: m001500run
        """
        # Extract the joint id from the serial output
        try:
            joint_id = int(serial_output[1])
        except Exception as e:
            print(f"Error extracting joint id from serial output: {e}")
            joint_id = -1

        # Extract the joint status from the serial output
        if "run" in serial_output:
            joint_status = "running"
        elif "done" in serial_output:
            joint_status = "done"
        else:
            print(f"Unknown joint status in serial output: {serial_output}")
            joint_status = "unknown"

        # Update the joint status   
        self.joints_status[joint_id] = joint_status

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

