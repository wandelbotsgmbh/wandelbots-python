import pytest

from wandelbots.types import IOValue


@pytest.mark.parametrize("value", [True, 1, 1.0, "a"])
def test_io_value(value):
    io = "test_io"
    io_value = IOValue.from_key_value(io, value)
    assert io_value.io == io
    assert io_value.as_dict() == {io: value}
    assert io_value.key == io
    assert io_value.value == value
