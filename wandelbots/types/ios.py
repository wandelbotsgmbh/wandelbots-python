from typing import Union

from wandelbots_api_client.models import IOValue

IOType = Union[bool, int, float, str]


class IOValue(IOValue):
    @classmethod
    def from_key_value(cls, key: str, value: IOType) -> IOValue:
        if isinstance(value, bool):
            return cls(io=key, boolean_value=value)
        elif isinstance(value, str):
            return cls(io=key, integer_value=value)
        elif isinstance(value, int):
            return cls(io=key, floating_value=value)
        elif isinstance(value, float):
            return cls(io=key, floating_value=value)
        else:
            raise ValueError(f"Value {value} is not a valid type for IOValue.")

    def as_dict(self) -> dict[str, IOType]:
        return {self.key: self.value}

    @property
    def key(self) -> str:
        return self.io

    @property
    def value(self) -> IOType:
        return self.integer_value or self.floating_value or self.boolean_value

    def __str__(self):
        return f"{self.key}: {self.value}"
