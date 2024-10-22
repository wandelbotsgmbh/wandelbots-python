import pytest
from wandelbots.core.instance import Instance

@pytest.fixture
def instance():
    return Instance()

def test_check_test_on_ipc(instance):
    assert instance.url == "http://api-gateway.wandelbots.svc.cluster.local:8080"