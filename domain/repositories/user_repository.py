from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.user import User
from domain.value_objects.email import Email
from domain.value_objects.user_id import UserId


class UserRepository(ABC):

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user"""
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Delete a user by ID"""
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users with pagination"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        pass
