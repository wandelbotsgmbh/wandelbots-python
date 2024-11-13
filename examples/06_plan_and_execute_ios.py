import asyncio
import logging
import os

from dotenv import load_dotenv

from wandelbots import Instance, MotionGroup, Planner
from wandelbots.exceptions import PlanningFailedException, PlanningPartialSuccessWarning
from wandelbots.types import Pose
from wandelbots.util.logger import setup_logging

load_dotenv()  # Load environment variables from .env
setup_logging(level=logging.INFO)


DEFAULT_IO = "digital_out[0]"


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
    target_pose = current_pose * Pose.from_list([0, 0, 100, 0, 0, 0])

    # Plan a line motion to the target pose
    planner = Planner(motion_group=my_robot)
    trajectory = [
        planner.set_io(key=DEFAULT_IO, value=True),
        planner.line(pose=target_pose),
        planner.set_io(key=DEFAULT_IO, value=False),
        planner.line(pose=current_pose),
        planner.set_io(key=DEFAULT_IO, value=True),
        planner.line(pose=target_pose),
        planner.set_io(key=DEFAULT_IO, value=False),
        planner.line(pose=current_pose),
        planner.set_io(key=DEFAULT_IO, value=True),
    ]

    # Try to plan the desired trajectory asynchronously
    try:
        plan_result = await planner.plan_async(
            trajectory=trajectory, start_joints=my_robot.current_joints()
        )
    except (PlanningFailedException, PlanningPartialSuccessWarning) as e:
        print(f"Planning failed: {e}")
        exit()

    # Execute the motion asynchronously without yielding current execution state
    print(f"Before execution {my_robot.get_io(DEFAULT_IO)=}")
    await my_robot.execute_motion_async(plan_result=plan_result, speed=10)
    print(f"After execution {my_robot.get_io(DEFAULT_IO)=}")


if __name__ == "__main__":
    asyncio.run(main())
