import uuid
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class UserId:
    value: str

    def __post_init__(self):
        if not self._is_valid_uuid(self.value):
            raise ValueError(f"Invalid UUID format: {self.value}")

    @classmethod
    def generate(cls) -> "UserId":
        return cls(str(uuid.uuid4()))

    def _is_valid_uuid(self, uuid_string: str) -> bool:
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Union["UserId", str]) -> bool:
        if isinstance(other, UserId):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False
