from typing import Optional

from wandelbots.core.instance import Instance
from wandelbots.request.syncs import get
from wandelbots.types import MotionGroupState, MotionGroupStateResponse, Pose, RobotTcps, TcpPose
from wandelbots.util.logger import _get_logger

logger = _get_logger(__name__)

_get_base_url = lambda url, cell: f"{url}/api/v1/cells/{cell}/motion-groups"


def get_tcps(instance: Instance, cell: str, motion_group: str) -> list[str]:
    url = f"{_get_base_url(instance.url, cell)}/{motion_group}/tcps"
    logger.debug(f"Getting tcps for cell {cell} and motion group {motion_group} on: {url}")
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to get tcps for cell {cell} and motion group {motion_group}")
        return []
    tcps = RobotTcps.from_dict(response).tcps
    return [tcp.id for tcp in tcps]


def get_current_joint_config(instance: Instance, cell: str, motion_group: str) -> list[float]:
    url = f"{_get_base_url(instance.url, cell)}/{motion_group}/state"
    logger.debug(
        f"Getting current joint config for cell {cell} and motion group {motion_group} on: {url}"
    )
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(
            f"Failed to get current joint config for cell {cell} and motion group {motion_group}"
        )
        return []
    motion_group_state: MotionGroupState = MotionGroupStateResponse.from_dict(response).state
    return motion_group_state.joint_position.joints


def get_current_tcp_pose(
    instance: Instance, cell: str, motion_group: str, tcp: str
) -> Optional[Pose]:
    url = f"{_get_base_url(instance.url, cell)}/{motion_group}/state?tcp={tcp}"
    logger.debug(
        f"Getting current tcp pose for cell {cell} and motion group {motion_group} and tcp {tcp} on: {url}"
    )
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(
            f"Failed to get current tcp pose for cell {cell} and motion group {motion_group}"
        )
        return None
    motion_group_state: MotionGroupState = MotionGroupStateResponse.from_dict(response).state
    tcp_pose: TcpPose = motion_group_state.tcp_pose
    return Pose(position=tcp_pose.position, orientation=tcp_pose.orientation)
