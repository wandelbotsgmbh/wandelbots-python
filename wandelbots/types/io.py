from wandelbots_api_client.models import IOValue
from typing import Union, Optional


class IOValue(IOValue):
    """Key-Value based data structure for representing I/O values"""

    io: str
    boolean_value: Optional[bool] = None
    integer_value: Optional[str] = None
    floating_value: Optional[float] = None

    @classmethod
    def from_key_value(cls, key: str, value: Union[bool, str, float]):
        if isinstance(value, bool):
            return cls(io=key, boolean_value=value)
        elif isinstance(value, str):
            return cls(io=key, integer_value=value)
        elif isinstance(value, float):
            return cls(io=key, floating_value=value)
        else:
            raise ValueError(f"Value {value} is not a valid type for IOValue")

    def as_dict(self) -> dict[str, Union[bool, str, float]]:
        return {self.key: self.value}

    @classmethod
    def from_dict(cls, io_dict: dict[str, Union[bool, str, float]]):
        k, v = list(io_dict.items())[0]
        return cls.from_key_value(k, v)

    @property
    def key(self) -> str:
        return self.io

    @property
    def value(self) -> Union[bool, str, float]:
        return self.integer_value or self.floating_value or self.boolean_value

    def __str__(self):
        return f"{self.key}: {self.value}"
