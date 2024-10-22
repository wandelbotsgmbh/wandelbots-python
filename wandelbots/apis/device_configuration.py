from wandelbots.core.instance import Instance
from wandelbots.request.syncs import get
from wandelbots.util.logger import _get_logger

logger = _get_logger(__name__)

_get_base_url = lambda url, cell: f"{url}/api/v1/cells/{cell}/devices"


def cell_is_available(instance: Instance, cell: str) -> bool:
    """check if cell is available by querying devices endpoint"""
    url = f"{_get_base_url(instance.url, cell)}"
    logger.debug(f"Checking if cell ({cell}) is available on: {url}")
    code, _ = get(url, instance=instance)
    return code == 200
