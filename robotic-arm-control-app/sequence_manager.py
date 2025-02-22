import time

class Pose:
    """
    Represents a pose of the robotic arm with joint values.
    """
    def __init__(self, joint_values):
        self.joint_values = joint_values.copy()  # Make a copy to avoid reference issues
    
    def __str__(self):
        return f"Pose(joints={self.joint_values})"

class SequenceManager:
    """
    Manage a sequence of poses for a robotic arm, handling execution and monitoring.
    """
    def __init__(self, serial_interface):
        self.serial_interface = serial_interface
        self.poses = []  # List to store poses
        self.interval = 1  # Default interval in seconds between poses
        self.is_playing = False
        self.current_pose_index = 0
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
        move_all_joints_command = ""
        for i, joint_value in enumerate(pose.joint_values):
            direction = "0" if joint_value >= 0 else "1"
            abs_value = abs(joint_value)
            move_all_joints_command += f"m{i}{direction}{abs_value}"

        return self.serial_interface.send_move_joint_command(move_all_joints_command)
    
    def play_sequence(self, back_and_forth=True):
        """Start playing the sequence"""
        if not self.poses:
            print("No poses in sequence")
            return False
        
        self.is_playing = True
        self.current_pose_index = 0
        self.play_direction = 1
        
        while self.is_playing:
            # Execute current pose
            print(f"## SequenceManager Class - Executing Pose Number => {self.current_pose_index + 1} / {len(self.poses)} <=")
            current_pose = self.poses[self.current_pose_index]
            self.execute_pose(current_pose)
            
            while True:
                time.sleep(0.1)
                #print(f"SequenceManager Class - Monitoring - Joints status: {self.serial_interface.joints_status}")
                if self.serial_interface.get_move_command_monitoring_done() is True:
                    break
            
            # Wait for interval
            print(f"## SequenceManager Class - Waiting between poses for => {self.interval} seconds...")
            time.sleep(self.interval)
            
            # Update index based on direction
            self.current_pose_index += self.play_direction
            
            # Handle direction changes if back_and_forth is True
            if back_and_forth:
                if self.current_pose_index >= len(self.poses):
                    self.current_pose_index = len(self.poses) - 2
                    self.play_direction = -1
                elif self.current_pose_index < 0:
                    self.current_pose_index = 1
                    self.play_direction = 1
            else:
                # Just loop from start if we reach the end
                if self.current_pose_index >= len(self.poses):
                    self.current_pose_index = 0
                
        return True
    
    def stop_sequence(self):
        """Stop the sequence playback"""
        self.is_playing = False
        print("Sequence playback stopped") 


