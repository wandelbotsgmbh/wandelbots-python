from wandelbots.core.instance import Instance
from wandelbots.request.syncs import get, post, delete
from wandelbots.util.logger import _get_logger
from wandelbots.types import MotionGroupInstanceList

logger = _get_logger(__name__)

_get_base_url = lambda url, cell: f"{url}/api/v1/cells/{cell}/motion-groups"


def get_active_motion_groups(instance: Instance, cell: str) -> list[str]:
    url = _get_base_url(instance.url, cell)
    logger.debug(f"Getting active motion groups for cell {cell} on: {url}")
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to get motion groups for cell {cell}")
        return []
    motion_group_instance_list = MotionGroupInstanceList.from_dict(response).instances
    return [instance.motion_group for instance in motion_group_instance_list]


def activate_motion_group(instance: Instance, cell: str, motion_group: str):
    # BUG: Why is the motion_group passed as a query parameter but in the deactivate function it is passed as a path parameter?
    url = f"{_get_base_url(instance.url, cell)}?motion_group={motion_group}"
    logger.debug(f"Activating motion group {motion_group} for cell {cell} on: {url}")
    code, _ = post(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to activate motion group {motion_group} for cell {cell}")


def deactivate_motion_group(instance: Instance, cell: str, motion_group: str):
    url = f"{_get_base_url(instance.url, cell)}/{motion_group}"
    logger.debug(f"Deactivating motion group {motion_group} for cell {cell} on: {url}")
    code = delete(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to deactivate motion group {motion_group} for cell {cell}")
