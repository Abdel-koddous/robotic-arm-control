"""
This module provides the user interface to retrieve path planning data from Moveit2.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout, QGridLayout, QLabel, QLineEdit, QGroupBox, QPushButton
import asyncio
import json
import websockets
import numpy as np   
from PyQt6.QtCore import QObject, QThread
import threading
from PyQt6.QtCore import pyqtSignal
class MoveitWebSocketWorker(QObject):
    """
    Worker class for handling Moveit2 websocket communication.
    """
    # Signals to communicate with the main GUI thread
    trajectory_received = pyqtSignal(list, list)  # initial_pose, target_pose
    connection_status_changed = pyqtSignal(str)  # status message
    error_occurred = pyqtSignal(str)  # error message
       
    # Windows & WSL ROS2 Bridge Info
    WSL_IP = "172.24.143.53"
    PORT = 9090
    URI = f"ws://{WSL_IP}:{PORT}"
    

    def __init__(self, wsl_ip=WSL_IP, port=PORT, topic_subscription=None):
        super().__init__()
        self.uri = f"ws://{wsl_ip}:{port}"
        self.topic_subscription = topic_subscription
        self.shutdown_event = threading.Event()

    def run(self):
        """
        Main Worker method
        Runs the asyncio event loop until the shutdown event is set.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._listen_websocket())
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            loop.close()
    
    async def _listen_websocket(self):
        """
        Asynchronous method to listen to the websocket.
        """
        try:
            self.connection_status_changed.emit("Connecting...")
            async with websockets.connect(self.uri) as ws:
                self.connection_status_changed.emit("Connected")
                # Subscribe to the topic
                await ws.send(json.dumps({
                    "op": "subscribe",
                    "topic": self.topic_subscription
                }))
                self.connection_status_changed.emit(f"Subscribed to {self.topic_subscription}")

                while not self.shutdown_event.is_set():
                    try:
                        # Use timeout to check stop condition periodically
                        raw_msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        json_msg = json.loads(raw_msg)
                        
                        # Parse trajectory data
                        if "msg" in json_msg and "trajectory" in json_msg["msg"]:
                            trajectory = json_msg["msg"]["trajectory"][0]
                            trajectory_points = trajectory["joint_trajectory"]["points"]
                            
                            if trajectory_points:
                                initial_pose = trajectory_points[0]["positions"]
                                target_pose = trajectory_points[-1]["positions"]
                                
                                # Convert to degrees
                                initial_deg = [np.round(np.rad2deg(pos), 2) for pos in initial_pose]
                                target_deg = [np.round(np.rad2deg(pos), 2) for pos in target_pose]
                                
                                # Emit signal with data
                                self.trajectory_received.emit(initial_deg, target_deg)
                    except asyncio.TimeoutError:
                        # Timeout error is expected when checking stop condition
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        break

        except Exception as e:
            self.error_occurred.emit(f"WebSocket error: {str(e)}")
        finally:
            self.connection_status_changed.emit("Disconnected")

    def stop(self):
        """Signal the worker to stop."""
        self.shutdown_event.set()

class Moveit2Interface(QWidget):
    """
    Interface for retrieving path planning data from Moveit2.
    """
    TOPIC_SUBSCRIBTION = "/display_planned_path"

    def __init__(self, joint_values, set_joints_config_callback = None, move_joints_callback = None):
        super().__init__()
        self.joint_values = joint_values
        self.set_joints_config_callback = set_joints_config_callback
        self.move_joints_callback = move_joints_callback

        self.websocket_worker = None
        self.websocket_thread = None

        self.init_ui()
        self.init_websocket_connection()

    def init_websocket_connection(self):
        """Initialize the websocket connection."""
        self.websocket_worker = MoveitWebSocketWorker(topic_subscription=self.TOPIC_SUBSCRIBTION)
        self.websocket_thread = QThread()
        self.websocket_worker.moveToThread(self.websocket_thread)

        # Connect signals and slots
        self.websocket_thread.started.connect(self.websocket_worker.run)
        self.websocket_worker.connection_status_changed.connect(self.update_connection_status)
        self.websocket_worker.trajectory_received.connect(self.update_trajectory)
        self.websocket_worker.error_occurred.connect(self.handle_websocket_error)

    def toggle_connection(self):
        """ Start or Stop the websocket connection."""
        if self.websocket_thread.isRunning():
            self.disconnect_from_moveit2()
        else:
            self.connect_to_moveit2()

    def connect_to_moveit2(self):
        """Connect to Moveit2."""
        self.websocket_thread.start()
        self.connect_button.setText("Disconnect from Moveit2")
    
    def disconnect_from_moveit2(self):
        """Disconnect from Moveit2."""
        if self.websocket_worker:
            self.websocket_worker.stop()
        if self.websocket_thread:
            self.websocket_thread.quit()
            self.websocket_thread.wait()
        self.connect_button.setText("Connect to Moveit2")
    
    def update_poses_from_moveit2(self, initial_deg, target_deg):
        """Update the poses from Moveit2."""
        self.initial_pose_input.setText(str(initial_deg))
        self.target_pose_input.setText(str(target_deg))

    def update_connection_status(self, status):
        """Update the connection status."""
        self.connection_status_label.setText(status)
        color = "green" if status == "Connected" else "red"
        self.connection_status_label.setStyleSheet(f"color: {color};")
    
    def update_trajectory(self, initial_deg, target_deg):
        """Update the trajectory."""
        self.initial_pose_input.setText(str(initial_deg))
        self.target_pose_input.setText(str(target_deg))

    def handle_websocket_error(self, error):
        """Handle the websocket error."""
        self.connection_status_label.setText(f"Error: {error}")
        self.connection_status_label.setStyleSheet("color: red;")

    def init_ui(self):
        """Initialize the user interface."""

        main_layout = QVBoxLayout()

        # Add connection controls
        connection_group = QGroupBox("MoveIt2 Connection")
        connection_group.setFixedHeight(150)
        connection_layout = QVBoxLayout()
        
        self.connect_button = QPushButton("Connect to MoveIt2")
        self.connect_button.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connect_button)
        
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet("color: red;")
        connection_layout.addWidget(self.connection_status_label)
        
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)

        # Initial Pose Section
        initial_pose_group = QGroupBox("Initial Pose")
        initial_pose_group.setFixedHeight(150)
        initial_pose_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: white;
            }
        """)
        initial_pose_layout = QVBoxLayout()
        
        # Single input field for initial pose as list
        initial_pose_label = QLabel("Initial Joint Values [joint1, joint2, joint3, joint4, joint5, joint6]")
        initial_pose_layout.addWidget(initial_pose_label)
        
        self.initial_pose_input = QLineEdit("[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]")
        self.initial_pose_input.setFixedWidth(300)
        initial_pose_layout.addWidget(self.initial_pose_input)
        
        initial_pose_group.setLayout(initial_pose_layout)
        main_layout.addWidget(initial_pose_group)
        
        # Target Pose Section
        target_pose_group = QGroupBox("Target Pose")
        target_pose_group.setFixedHeight(150)
        target_pose_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: white;
            }
        """)
        target_pose_layout = QVBoxLayout()
        
        # Single input field for target pose as list
        target_pose_label = QLabel("Target Joint Values [joint1, joint2, joint3, joint4, joint5, joint6]")
        target_pose_layout.addWidget(target_pose_label)
        
        self.target_pose_input = QLineEdit("[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]")
        self.target_pose_input.setFixedWidth(300)
        target_pose_layout.addWidget(self.target_pose_input)
        
        target_pose_group.setLayout(target_pose_layout)
        
        # Execute target pose button
        execute_button = QPushButton("Execute Target Pose")
        execute_button.setFixedHeight(30)
        execute_button.clicked.connect(self.move_joints_callback)
        target_pose_layout.addWidget(execute_button)
        
        main_layout.addWidget(target_pose_group)
        
        # Set the main layout
        self.setLayout(main_layout)
