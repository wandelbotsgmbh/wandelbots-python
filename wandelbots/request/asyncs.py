import httpx
from typing import Dict, Tuple, Optional
from wandelbots.util.logger import _get_logger
from wandelbots.request.config import TIMEOUT
from wandelbots.core.instance import Instance

__logger = _get_logger(__name__)


def _get_auth(instance: Instance) -> Optional[httpx.BasicAuth]:
    if instance.has_auth():
        return httpx.BasicAuth(username=instance.user, password=instance.password)
    return None


def _handle_request_error(err):
    if isinstance(err, httpx.HTTPStatusError):
        if err.response.status_code == 401:
            __logger.error("401 Unauthorized access. Check your credentials.")
        else:
            __logger.error(
                f"HTTP error occurred: {err} - Response content: {err.response.text}"
            )
    elif isinstance(err, httpx.ConnectTimeout):
        __logger.error(f"Connection timeout error occurred: {err}")
    elif isinstance(err, httpx.RequestError):
        __logger.error(f"Request error occurred: {err}")


async def get(url: str, instance: Instance) -> Tuple[int, Optional[Dict]]:
    async with httpx.AsyncClient(auth=_get_auth(instance)) as client:
        try:
            response = await client.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.status_code, response.json()
        except (httpx.HTTPStatusError, httpx.ConnectTimeout, httpx.RequestError) as err:
            _handle_request_error(err)
        return 500, None


async def delete(url: str, instance: Instance) -> int:
    async with httpx.AsyncClient(auth=_get_auth(instance)) as client:
        try:
            response = await client.delete(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.status_code
        except (httpx.HTTPStatusError, httpx.ConnectTimeout, httpx.RequestError) as err:
            _handle_request_error(err)
        return 500


async def post(
    url: str, instance: Instance, data: Dict = {}
) -> Tuple[int, Optional[Dict]]:
    async with httpx.AsyncClient(auth=_get_auth(instance)) as client:
        try:
            response = await client.post(url, json=data, timeout=TIMEOUT)
            response.raise_for_status()
            return response.status_code, response.json()
        except (httpx.HTTPStatusError, httpx.ConnectTimeout, httpx.RequestError) as err:
            _handle_request_error(err)
        return 500, None


async def put(
    url: str, instance: Instance, data: Dict = {}
) -> Tuple[int, Optional[Dict]]:
    async with httpx.AsyncClient(auth=_get_auth(instance)) as client:
        try:
            response = await client.put(url, json=data, timeout=TIMEOUT)
            response.raise_for_status()
            return response.status_code, response.json()
        except (httpx.HTTPStatusError, httpx.ConnectTimeout, httpx.RequestError) as err:
            _handle_request_error(err)
        return 500, None
