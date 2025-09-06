"""
Capture the joint states from the Moveit2 interface and use them to control the robotic arm.
"""
import asyncio
import json
import websockets
import numpy as np
async def listen():
    """
    Listen to the /display_planned_path topic and print the joint positions of the last trajectory point.
    """
    # Use ws://localhost:9090 if it works, otherwise ws://<wsl_ip>:9090
    wsl_ip = "172.24.143.53"
    port = 9090
    uri = f"ws://{wsl_ip}:{port}"

    async with websockets.connect(uri) as ws:
        # Subscribe to /chatter topic
        await ws.send(json.dumps({
            "op": "subscribe",
            "topic": "/display_planned_path"
        }))

        print("Subscribed to /joint_states, waiting for messages...\n")
        while True:
            raw_msg = await ws.recv()
            json_msg = json.loads(raw_msg)
            print("======================================================")
            print("Received JSON message payload:", json_msg["msg"].keys())
            trajectory = json_msg["msg"]["trajectory"][0]
            print("Type of trajectory field:", type(trajectory))
            print("Keys of trajectory field:", trajectory.keys())

            print("Joint names in the trajectory:", trajectory["joint_trajectory"]["joint_names"])
            trajectory_points = trajectory["joint_trajectory"]["points"]
            print("Type of trajectory_points field:", type(trajectory_points))
            print("Number of trajectory points:", len(trajectory_points))
            initial_pose = trajectory_points[0]["positions"]
            target_pose = trajectory_points[-1]["positions"]

            print("Joint positions of the last trajectory point:", target_pose)
            initial_pose_deg = [np.round(np.rad2deg(pose), 2) for pose in initial_pose]
            target_pose_deg = [np.round(np.rad2deg(pose), 2) for pose in target_pose]
            print("Joint positions of the initial trajectory point in degrees:", initial_pose_deg)
            print("Joint positions of the last trajectory point in degrees:", target_pose_deg)

asyncio.run(listen())
