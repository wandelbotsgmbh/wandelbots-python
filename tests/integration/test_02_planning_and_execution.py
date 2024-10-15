import pytest
import os
import asyncio
from wandelbots import Instance, MotionGroup, Planner
from wandelbots.exceptions import MotionExecutionInterruptedError
from wandelbots.types import Vector3d as v


@pytest.mark.asyncio
async def test_motion_planning_and_execution():
    """Test planning and executing a motion against the actual motion-group backend."""
    
    instance = Instance(
        url=os.getenv("WANDELAPI_BASE_URL"),
        user=os.getenv("NOVA_USERNAME"),
        password=os.getenv("NOVA_PASSWORD"),
    )

    motion_group = MotionGroup(
        instance=instance,
        cell=os.getenv("CELL_ID"),
        motion_group=os.getenv("MOTION_GROUP"),
        default_tcp=os.getenv("TCP"),
    )

    # Set up planner and motion-group state
    planner = Planner(motion_group)
    home = [0, -1.571, 1.571, -1.571, -1.571, 0]
    current_pose = motion_group.current_tcp_pose()

    # Translate current TCP pose and plan a motion
    current_pose.translate(vector=v(x=0, y=0, z=-500))
    trajectory = [
        planner.jptp(joints=home),
        planner.line(pose=current_pose),
        planner.jptp(joints=home),
    ]
    plan_result = planner.plan(
        start_joints=motion_group.current_joints(), trajectory=trajectory
    )

    # Check if the motion plan was successful
    assert plan_result.motion is not None, "Failed to plan motion"
    
    # Execute planned motion
    async def execute_in_background(motion: str, speed: int):
        try:
            async for move_response in motion_group.execute_motion_stream_async(motion, speed):
                print(move_response)
        except MotionExecutionInterruptedError:
            print("Motion execution was interrupted")
        except Exception as e:
            pytest.fail(f"Error during motion execution: {str(e)}")

    motion_task = asyncio.create_task(execute_in_background(plan_result.motion, 50))

    # Allow the motion to run for 2 seconds, then stop
    await asyncio.sleep(2)
    motion_group.stop()
    await motion_task
    assert not motion_group.is_executing(), "Motion-group should not be executing motion after stop command"