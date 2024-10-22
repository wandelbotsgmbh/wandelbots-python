from wandelbots.types import IOValue


def test_io_value():
    io = "test_io"
    value = 42
    io_value = IOValue.from_key_value(io, value)
    assert io_value.io == io
    assert io_value.integer_value == value
    assert io_value.as_dict() == {io: value}
    assert io_value.key == io
    assert io_value.value == value
    assert io_value == IOValue.from_dict({io: value})
