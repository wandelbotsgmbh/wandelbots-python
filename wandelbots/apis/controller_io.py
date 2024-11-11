from wandelbots.core.instance import Instance
from wandelbots.request.syncs import put, get
from wandelbots.util.logger import _get_logger
from wandelbots.types import IOValue


logger = _get_logger(__name__)

_get_base_url = lambda url, cell: f"{url}/api/v1/cells/{cell}/controllers"


def set_values(instance: Instance, cell: str, controller: str, values: list[IOValue]) -> None:
    url = f"{_get_base_url(instance.url, cell)}/{controller}/ios/values"
    data = [io.model_dump() for io in values]
    code, _ = put(url, data=data, instance=instance)
    if code != 200:
        logger.error(f"Failed to set values for controller {controller}")
    else:
        logger.debug(f"Successfully set values for controller {controller}: {values}")


def get_values(instance: Instance, cell: str, controller: str, ios: list[str]) -> list[IOValue]:
    url = f"{_get_base_url(instance.url, cell)}/{controller}/ios/values?ios={'&ios='.join(ios)}"
    code, response = get(url, instance=instance)
    if code != 200:
        logger.error(f"Failed to get values for controller {controller}")
    else:
        logger.debug(f"Successfully get values for controller {controller}: {ios}")
    return [IOValue(**io) for io in response["io_values"]]
