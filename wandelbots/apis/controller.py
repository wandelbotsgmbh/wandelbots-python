from typing import Optional

from wandelbots.core.instance import Instance
from wandelbots.request.syncs import get, put
from wandelbots.util.logger import _get_logger
from wandelbots.types import ControllerInstanceList, GetModeResponse

logger = _get_logger(__name__)

_get_base_url = lambda url, cell: f"{url}/api/v1/cells/{cell}/controllers"


def get_controllers(instance: Instance, cell: str) -> list[str]:
    url = f"{_get_base_url(instance.url, cell)}"
    logger.debug(f"Getting controllers for cell {cell} on: {url}")
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to get controllers for cell {cell}")
        return []
    instances = ControllerInstanceList.from_dict(response).instances
    return [instance.controller for instance in instances]


def set_default_mode(instance: Instance, cell: str, controller: str, mode: str) -> None:
    url = f"{_get_base_url(instance.url, cell)}/{controller}/mode?mode={mode}"
    code, _ = put(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to set default mode to {mode} for controller {controller}")


def get_current_mode(instance: Instance, cell: str, controller: str) -> Optional[str]:
    url = f"{_get_base_url(instance.url, cell)}/{controller}/mode"
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to get current mode for controller {controller}")
        return None
    mode = GetModeResponse.from_dict(response).robot_system_mode
    return mode
