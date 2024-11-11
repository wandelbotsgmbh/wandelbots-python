import os
import logging
import asyncio

from dotenv import load_dotenv

from wandelbots import Instance, MotionGroup, Planner
from wandelbots.types import Pose, Vector3d
from wandelbots.exceptions import (
    PlanningFailedException,
    PlanningPartialSuccessWarning,
    MotionExecutionInterruptedError,
)
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


async def main():
    # Get current TCP pose and offset it slightly along the z-axis
    current_pose: Pose = my_robot.current_tcp_pose()
    target_pose = current_pose.translate(Vector3d(z=100))

    # Plan a line motion to the target pose
    planner = Planner(motion_group=my_robot)
    trajectory = [planner.line(pose=target_pose)]

    # Try to plan the desired trajectory asynchronously
    try:
        plan_result = await planner.plan_async(
            trajectory=trajectory, start_joints=my_robot.current_joints()
        )
    except (PlanningFailedException, PlanningPartialSuccessWarning) as e:
        print(f"Planning failed: {e}")
        exit()

    # Now we can execute a motion in the background in a non-blocking way,
    # by defining a function that will be executed as a task
    async def execute_in_background(motion: str, speed: int):
        try:
            async for state in my_robot.execute_motion_stream_async(motion, speed):
                time_until_complete = state.time_to_end
                print(f"Motion done in: {time_until_complete/1000} s")
        except (
            MotionExecutionInterruptedError
        ):  # This has to be in here to catch motion interruptions by the user
            pass
        except Exception as e:
            print(f"An error occurred during execution: {e}")

    # Create a task that will execute the motion in the background
    motion_task = asyncio.create_task(execute_in_background(plan_result.motion, 5))

    # Pretend to some other work
    await asyncio.sleep(2)

    # Stop the motion and check that it is no longer executing
    my_robot.stop()
    await motion_task
    print(f"Robot is executing motion: {my_robot.is_executing()}")


if __name__ == "__main__":
    asyncio.run(main())
