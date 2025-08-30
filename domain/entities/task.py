from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from domain.value_objects.task_id import TaskId
from domain.value_objects.user_id import UserId


@dataclass
class Task:
    id: TaskId
    user_id: UserId
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls, user_id: UserId, title: str, description: Optional[str] = None
    ) -> "Task":
        if not title or len(title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        if description and len(description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")

        return cls(
            id=TaskId.generate(),
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
        )

    def update_title(self, new_title: str) -> None:
        if not new_title or len(new_title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(new_title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        self.title = new_title.strip()
        self.updated_at = datetime.now(timezone.utc)

    def update_description(self, new_description: Optional[str]) -> None:
        if new_description and len(new_description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
        self.description = new_description.strip() if new_description else None
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        if self.completed:
            return  # Already completed
        self.completed = True
        self.updated_at = datetime.now(timezone.utc)

    def mark_incomplete(self) -> None:
        if not self.completed:
            return  # Already incomplete
        self.completed = False
        self.updated_at = datetime.now(timezone.utc)

    def belongs_to_user(self, user_id: UserId) -> bool:
        return self.user_id == user_id
