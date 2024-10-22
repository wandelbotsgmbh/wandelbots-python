import pytest
from wandelbots.core.instance import Instance

@pytest.fixture
def instance():
    return Instance()

def test_check_test_on_ipc(instance):
    assert instance.url == "http://api-gateway:8080"