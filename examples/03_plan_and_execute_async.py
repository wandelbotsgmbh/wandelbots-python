import os
import logging
import asyncio

from dotenv import load_dotenv

from wandelbots import Instance, MotionGroup, Planner
from wandelbots.types import Pose, Vector3d
from wandelbots.exceptions import PlanningFailedException, PlanningPartialSuccessWarning
from wandelbots.util.logger import setup_logging

load_dotenv()  # Load environment variables from .env
setup_logging(level=logging.INFO)


my_instance = Instance(
    url=os.getenv("WANDELAPI_BASE_URL"),
    user=os.getenv("NOVA_USERNAME"),
    password=os.getenv("NOVA_PASSWORD"),
)

my_robot = MotionGroup(
    instance=my_instance,
    cell=os.getenv("CELL_ID"),
    motion_group=os.getenv("MOTION_GROUP"),
    default_tcp=os.getenv("TCP"),
)


async def main():

    # Get current TCP pose and offset it slightly along the z-axis
    current_pose: Pose = my_robot.current_tcp_pose()
    target_pose = current_pose.translate(Vector3d(z=100))

    # Plan a line motion to the target pose
    planner = Planner(motion_group=my_robot)
    trajectory = [
        planner.line(pose=target_pose),
    ]

    # Try to plan the desired trajectory asynchronously
    try:
        plan_result = await planner.plan_async(
            trajectory=trajectory,
            start_joints=my_robot.current_joints(),
        )
    except (PlanningFailedException, PlanningPartialSuccessWarning) as e:
        print(f"Planning failed: {e}")
        exit()

    # Execute the motion asynchronously without yielding current execution state
    motion = plan_result.motion
    await my_robot.execute_motion_async(motion=motion, speed=10)

    # A motion can also be executed leveraging a bi-directional approach,
    # thus yielding the current execution state.
    # Here we just playback the same motion backwards
    async for state in my_robot.execute_motion_stream_async(
        motion=motion, speed=10, direction="backward"
    ):
        time_until_complete = state.time_to_end
        print(f"Motion done in: {time_until_complete/1000} s")


if __name__ == "__main__":
    asyncio.run(main())
