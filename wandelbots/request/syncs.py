from typing import Dict, Optional, Tuple

import httpx
import requests

from wandelbots.core.instance import Instance
from wandelbots.request.config import TIMEOUT
from wandelbots.util.logger import _get_logger

__logger = _get_logger(__name__)


def _get_auth_header(instance: Instance) -> Optional[Dict[str, str]]:
    if instance.has_access_token():
        return {"Authorization": f"Bearer {instance.access_token}"}
    return None


def _get_auth(instance: Instance) -> Optional[httpx.BasicAuth]:
    if instance.has_basic_auth():
        return requests.auth.HTTPBasicAuth(username=instance.user, password=instance.password)
    return None


def _handle_request_error(err):
    if isinstance(err, requests.HTTPError):
        if err.response.status_code == 401:
            __logger.error("401 Unauthorized access. Check your credentials.")
        else:
            __logger.error(f"HTTP error occurred: {err} - Response content: {err.response.text}")
    elif isinstance(err, requests.ConnectionError):
        __logger.error(f"Connection error occurred: {err}")
    elif isinstance(err, requests.Timeout):
        __logger.error(f"Timeout error occurred: {err}")
    elif isinstance(err, requests.RequestException):
        __logger.error(f"Request error occurred: {err}")


def get(url: str, instance: Instance) -> Tuple[int, Optional[Dict]]:
    try:
        response = requests.get(
            url, timeout=TIMEOUT, headers=_get_auth_header(instance), auth=_get_auth(instance)
        )
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.RequestException as err:
        _handle_request_error(err)
    return 500, None


def delete(url: str, instance: Instance) -> int:
    try:
        response = requests.delete(
            url, timeout=TIMEOUT, headers=_get_auth_header(instance), auth=_get_auth(instance)
        )
        response.raise_for_status()
        return response.status_code
    except requests.RequestException as err:
        _handle_request_error(err)
    return 500


def post(url: str, instance: Instance, data: Dict = {}) -> Tuple[int, Optional[Dict]]:
    try:
        response = requests.post(
            url,
            json=data,
            timeout=TIMEOUT,
            headers=_get_auth_header(instance),
            auth=_get_auth(instance),
        )
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.RequestException as err:
        _handle_request_error(err)
    return 500, None


def put(url: str, instance: Instance, data: Dict = {}) -> Tuple[int, Optional[Dict]]:
    try:
        response = requests.put(
            url,
            json=data,
            timeout=TIMEOUT,
            headers=_get_auth_header(instance),
            auth=_get_auth(instance),
        )
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.RequestException as err:
        _handle_request_error(err)
    return 500, None
