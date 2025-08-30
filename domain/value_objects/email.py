import re
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    def _is_valid_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Union["Email", str]) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False
