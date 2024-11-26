import asyncio
import logging
import os

from dotenv import load_dotenv

from wandelbots import Instance, MotionGroup, Planner
from wandelbots.apis import motion_group as motion_group_api
from wandelbots.apis import motion_group_infos as motion_group_infos_api
from wandelbots.types import Pose
from wandelbots.util.logger import setup_logging

load_dotenv()  # Load environment variables from .env
setup_logging(level=logging.INFO)

# this example needs two virtual robots in your instance
my_instance = Instance(
    url=os.getenv("WANDELAPI_BASE_URL"),
    user=os.getenv("NOVA_USERNAME"),
    password=os.getenv("NOVA_PASSWORD"),
)

motion_groups = motion_group_api.get_active_motion_groups(
    instance=my_instance, cell=os.getenv("CELL_ID")
)

# first robot
motion_group_one_id = motion_groups[0]
tcps_one = motion_group_infos_api.get_tcps(
    instance=my_instance, cell=os.getenv("CELL_ID"), motion_group=motion_group_one_id
)
tcp_one = tcps_one[0]

my_robot_one = MotionGroup(
    instance=my_instance,
    cell=os.getenv("CELL_ID"),
    motion_group=motion_group_one_id,
    default_tcp=tcp_one,
)

# second robot
motion_group_two_id = motion_groups[0]
tcps_two = motion_group_infos_api.get_tcps(
    instance=my_instance, cell=os.getenv("CELL_ID"), motion_group=motion_group_two_id
)
tcp_two = tcps_one[0]

my_robot_two = MotionGroup(
    instance=my_instance,
    cell=os.getenv("CELL_ID"),
    motion_group=motion_group_two_id,
    default_tcp=tcp_two,
)


async def main():
    # Plan a line motion to the target pose for robot one
    current_pose_one: Pose = my_robot_one.current_tcp_pose()
    target_pose_one = current_pose_one * Pose.from_list([0, 0, 100, 0, 0, 0])

    planner_one = Planner(motion_group=my_robot_one)
    trajectory_one = [
        planner_one.line(pose=target_pose_one),
        planner_one.line(pose=current_pose_one),
        planner_one.line(pose=target_pose_one),
        planner_one.line(pose=current_pose_one),
    ]
    plan_result_one = planner_one.plan(
        start_joints=my_robot_one.current_joints(), trajectory=trajectory_one
    )

    # Plan a line motion to the target pose for robot two
    current_pose_two: Pose = my_robot_two.current_tcp_pose()
    target_pose_two = current_pose_two * Pose.from_list([0, 0, 100, 0, 0, 0])

    planner_two = Planner(motion_group=my_robot_two)
    trajectory_two = [
        planner_two.line(pose=target_pose_two),
        planner_two.line(pose=current_pose_two),
        planner_two.line(pose=target_pose_two),
        planner_two.line(pose=current_pose_two),
    ]
    plan_result_two = planner_two.plan(
        start_joints=my_robot_two.current_joints(), trajectory=trajectory_two
    )

    await asyncio.gather(
        my_robot_one.execute_motion_async(motion=plan_result_one.motion, speed=25),
        my_robot_two.execute_motion_async(motion=plan_result_two.motion, speed=25),
    )


if __name__ == "__main__":
    asyncio.run(main())
