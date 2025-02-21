import time

class Pose:
    def __init__(self, joint_values):
        self.joint_values = joint_values.copy()  # Make a copy to avoid reference issues
    
    def __str__(self):
        return f"Pose(joints={self.joint_values})"

class SequenceManager:
    def __init__(self, serial_interface):
        self.serial_interface = serial_interface
        self.poses = []  # List to store poses
        self.interval = 2  # Default interval in seconds between poses
        self.is_playing = False
        self.play_direction = 1  # 1 for forward, -1 for backward
    
    def add_pose(self, joint_values):
        """Add a new pose to the sequence"""
        pose = Pose(joint_values)
        self.poses.append(pose)
        # print(f"Added pose: {pose}")
        return len(self.poses) - 1  # Return index of added pose
    
    def remove_pose(self, index):
        """Remove a pose at given index"""
        if 0 <= index < len(self.poses):
            removed = self.poses.pop(index)
            print(f"Removed pose at index {index}: {removed}")
            return True
        return False
    
    def clear_sequence(self):
        """Clear all poses"""
        self.poses = []
        print("Sequence cleared")
    
    def set_interval(self, seconds):
        """Set the interval between poses"""
        self.interval = max(0.1, float(seconds))  # Minimum 0.1 seconds
        print(f"Interval set to {self.interval} seconds")
    
    def get_pose(self, index):
        """Get pose at specific index"""
        if 0 <= index < len(self.poses):
            return self.poses[index]
        return None
    
    def execute_pose(self, pose):
        """Execute a single pose"""
        command = "".join([f"m{i}0{val}" for i, val in enumerate(pose.joint_values)])
        print(f"Executing command: {command}")

        if not self.serial_interface.serial_connection.is_open:
            self.serial_interface.connect()
        
        return self.serial_interface.send_move_joint_command(command)
    
    def play_sequence(self, back_and_forth=True):
        """Start playing the sequence"""
        if not self.poses:
            print("No poses in sequence")
            return False
        
        self.is_playing = True
        current_index = 0
        self.play_direction = 1
        
        while self.is_playing:
            # Execute current pose
            current_pose = self.poses[current_index]
            self.execute_pose(current_pose)
            
            while True:
                time.sleep(0.1)
                #print(f"SequenceManager Class - Monitoring - Joints status: {self.serial_interface.joints_status}")
                if self.serial_interface.get_move_command_monitoring_done() is True:
                    break
            
            # Wait for interval
            print(f"SequenceManager Class - Waiting between poses for => {self.interval} seconds...")
            time.sleep(self.interval)
            
            # Update index based on direction
            current_index += self.play_direction
            
            # Handle direction changes if back_and_forth is True
            if back_and_forth:
                if current_index >= len(self.poses):
                    current_index = len(self.poses) - 2
                    self.play_direction = -1
                elif current_index < 0:
                    current_index = 1
                    self.play_direction = 1
            else:
                # Just loop from start if we reach the end
                if current_index >= len(self.poses):
                    current_index = 0
                
        return True
    
    def stop_sequence(self):
        """Stop the sequence playback"""
        self.is_playing = False
        print("Sequence playback stopped") 


