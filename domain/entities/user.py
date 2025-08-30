from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from domain.value_objects.email import Email
from domain.value_objects.user_id import UserId


@dataclass
class User:
    id: UserId
    email: Email
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @classmethod
    def create(cls, email: Email, username: str, hashed_password: str) -> "User":
        return cls(
            id=UserId.generate(),
            email=email,
            username=username,
            hashed_password=hashed_password,
        )

    def update_username(self, new_username: str) -> None:
        if not new_username or len(new_username.strip()) == 0:
            raise ValueError("Username cannot be empty")
        self.username = new_username.strip()
        self.updated_at = datetime.now(timezone.utc)

    def update_email(self, new_email: Email) -> None:
        self.email = new_email
        self.updated_at = datetime.now(timezone.utc)

    def update_password(self, new_hashed_password: str) -> None:
        if not new_hashed_password:
            raise ValueError("Hashed password cannot be empty")
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
