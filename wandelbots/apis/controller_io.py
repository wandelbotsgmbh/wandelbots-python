from wandelbots.core.instance import Instance
from wandelbots.request.syncs import put
from wandelbots.util.logger import _get_logger

logger = _get_logger(__name__)

_get_base_url = lambda url, cell: f"{url}/api/v1/cells/{cell}/controllers"


def set_values(
    instance: Instance, cell: str, controller: str, values: list[dict]
) -> None:
    url = f"{_get_base_url(instance.url, cell)}/{controller}/ios/values"
    code, _ = put(url, data=values, instance=instance)
    if code != 200:
        logger.error(f"Failed to set values for controller {controller}")
    else:
        logger.debug(f"Successfully set values for controller {controller}: {values}")
