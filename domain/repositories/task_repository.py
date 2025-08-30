from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.task import Task
from domain.value_objects.task_id import TaskId
from domain.value_objects.user_id import UserId


class TaskRepository(ABC):

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Create a new task"""
        pass

    @abstractmethod
    async def get_by_id(self, task_id: TaskId) -> Optional[Task]:
        """Get task by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        """Get all tasks for a specific user with pagination"""
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Update an existing task"""
        pass

    @abstractmethod
    async def delete(self, task_id: TaskId) -> bool:
        """Delete a task by ID"""
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UserId) -> int:
        """Count tasks for a specific user"""
        pass

    @abstractmethod
    async def get_completed_by_user_id(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        """Get completed tasks for a specific user"""
        pass

    @abstractmethod
    async def get_pending_by_user_id(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        """Get pending tasks for a specific user"""
        pass
