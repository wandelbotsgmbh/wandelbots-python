import logging
import os

import numpy as np
from dotenv import load_dotenv

from wandelbots import Instance, MotionGroup, Planner
from wandelbots.exceptions import PlanningFailedException, PlanningPartialSuccessWarning
from wandelbots.types import Pose, Vector3d
from wandelbots.util.logger import setup_logging

load_dotenv()  # Load environment variables from .env
setup_logging(level=logging.INFO)


my_instance = Instance(
    url=os.getenv("WANDELAPI_BASE_URL"), access_token=os.getenv("NOVA_ACCESS_TOKEN")
)

my_robot = MotionGroup(
    instance=my_instance,
    cell=os.getenv("CELL_ID"),
    motion_group=os.getenv("MOTION_GROUP"),
    default_tcp=os.getenv("TCP"),
)

if __name__ == "__main__":
    # Define a home position
    home_joints = [0, -np.pi / 2, -np.pi / 2, -np.pi / 2, np.pi / 2, 0]
    # [0, -90, -90, -90, 90, 0]

    # Get current TCP pose and offset it slightly along the x-axis
    current_pose: Pose = my_robot.current_tcp_pose()
    target_pose = current_pose.translate(Vector3d(x=100))

    # Plan a motion home -> target_pose -> home
    planner = Planner(motion_group=my_robot)
    trajectory = [
        planner.joint_ptp(joints=home_joints),
        planner.cartesian_ptp(pose=target_pose),
        planner.joint_ptp(joints=home_joints),
    ]

    # Try to plan the desired trajectory
    try:
        plan_result = planner.plan(trajectory=trajectory, start_joints=my_robot.current_joints())
    except (PlanningFailedException, PlanningPartialSuccessWarning) as e:
        print(f"Planning failed: {e}")
        exit()

    # Execute the motion
    my_robot.execute_motion(plan_result=plan_result, speed=100)
    print("Done!")
