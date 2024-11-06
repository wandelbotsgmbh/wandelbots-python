import pytest
import os
from wandelbots import Instance, MotionGroup


@pytest.mark.asyncio
async def test_motion_group_initialization():
    """Test motion-group initialization and retrieve basic state from the actual backend."""
    instance = Instance(
        url=os.getenv("WANDELAPI_BASE_URL"),
        access_token=os.getenv("NOVA_ACCESS_TOKEN"),
    )

    motion_group = MotionGroup(
        instance=instance,
        cell=os.getenv("CELL_ID"),
        motion_group=os.getenv("MOTION_GROUP"),
        default_tcp=os.getenv("TCP"),
    )

    # Fetch basic state
    tcps = motion_group.tcps()
    joints = motion_group.current_joints()
    tcp_pose = motion_group.current_tcp_pose()

    # Assertions to ensure data is fetched
    assert isinstance(tcps, list), "Expected a list of TCPs"
    assert len(tcps) > 0, "TCP list should not be empty"
    assert isinstance(joints, list), "Expected a list of joints"
    assert len(joints) == 6, "Expected 6 joint values"
    assert tcp_pose is not None, "TCP pose should not be None"
