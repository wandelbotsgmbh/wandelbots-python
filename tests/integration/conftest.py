import pytest
import requests
import os
from dotenv import load_dotenv, find_dotenv
import requests.auth


def get_auth_token() -> dict[str, str]:
    token = os.getenv("NOVA_ACCESS_TOKEN")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}


def get_basic_auth() -> requests.auth.HTTPBasicAuth:
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")
    if not username or not password:
        return None
    return requests.auth.HTTPBasicAuth(username, password)


@pytest.fixture(scope="session", autouse=True)
def check_test_motion_group_available(request):

    # Get config from .env file
    test_env = find_dotenv("envs/.env.tests")
    load_dotenv(test_env)

    # Check if the environment is set correctly
    nova_host = os.getenv("WANDELAPI_BASE_URL")
    if not nova_host:
        pytest.fail("WANDELAPI_BASE_URL not set in the environment.")

    # General availability check
    try:
        headers = get_auth_token()
        auth = get_basic_auth()

        if "wandelbots.io" in nova_host and not headers and not auth:
            pytest.fail(
                "Please provide NOVA_ACCESS_TOKEN or NOVA_USERNAME and NOVA_PASSWORD in the environment (depending on the used auth method)."
            )

        response = requests.get(nova_host, timeout=5, headers=headers, auth=auth)
        response.raise_for_status()
    except requests.RequestException as e:
        skip_reason = f"Skipping tests: Backend service is not available at {nova_host}. Error: {e}"
        pytest.skip(skip_reason)

    # Check Cell, Motion Group, and TCP availability in environment
    cell = os.getenv("CELL_ID")
    motion_group = os.getenv("MOTION_GROUP")
    tcp = os.getenv("TCP")
    if not (cell and motion_group and tcp):
        pytest.fail(
            "Required environment variables CELL_ID, MOTION_GROUP, or TCP are missing."
        )

    # Check Cell, Motion Group, and TCP availability in nova service
    endpoint_url = (
        f"{nova_host}/api/v1/cells/{cell}/motion-groups/{motion_group}/state?tcp={tcp}"
    )
    try:
        response = requests.get(endpoint_url, timeout=5, headers=headers, auth=auth)
        response.raise_for_status()
    except requests.HTTPError as e:
        try:
            error_message = response.json().get("message", "Unknown error")
            skip_reason = f"Skipping tests: {error_message}. Response Code: {response.status_code}"
        except ValueError:
            skip_reason = f"Skipping tests: Non-JSON response. Response Code: {response.status_code}, Error: {str(e)}"
        pytest.skip(skip_reason)
    except requests.RequestException as e:
        skip_reason = f"Skipping tests: {str(e)}"
        pytest.skip(skip_reason)
