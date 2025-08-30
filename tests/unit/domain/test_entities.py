"""
Unit tests for domain entities.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from domain.entities.task import Task
from domain.entities.user import User
from domain.value_objects.email import Email
from domain.value_objects.task_id import TaskId
from domain.value_objects.user_id import UserId


class TestUser:
    """Tests for User entity."""

    def test_create_user(self):
        """Test creating a user with the create class method."""
        email = Email("test@example.com")
        username = "testuser"
        hashed_password = "hashed_password_123"

        with patch("domain.value_objects.user_id.UserId.generate") as mock_generate:
            mock_id = UserId("123e4567-e89b-12d3-a456-426614174000")
            mock_generate.return_value = mock_id

            user = User.create(email, username, hashed_password)

            assert user.id == mock_id
            assert user.email == email
            assert user.username == username
            assert user.hashed_password == hashed_password
            assert user.is_active is True
            assert isinstance(user.created_at, datetime)
            assert user.updated_at is None

    def test_update_username(self):
        """Test updating username."""
        email = Email("test@example.com")
        user = User.create(email, "olduser", "hashed_password")
        original_updated_at = user.updated_at

        with patch("domain.entities.user.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            user.update_username("newuser")

            assert user.username == "newuser"
            assert user.updated_at == mock_now
            assert user.updated_at != original_updated_at

    def test_update_username_empty(self):
        """Test updating username with empty value raises error."""
        email = Email("test@example.com")
        user = User.create(email, "testuser", "hashed_password")

        with pytest.raises(ValueError, match="Username cannot be empty"):
            user.update_username("")

        with pytest.raises(ValueError, match="Username cannot be empty"):
            user.update_username("   ")  # Only whitespace

    def test_update_email(self):
        """Test updating email."""
        old_email = Email("old@example.com")
        new_email = Email("new@example.com")
        user = User.create(old_email, "testuser", "hashed_password")

        with patch("domain.entities.user.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            user.update_email(new_email)

            assert user.email == new_email
            assert user.updated_at == mock_now

    def test_update_password(self):
        """Test updating password."""
        email = Email("test@example.com")
        user = User.create(email, "testuser", "old_hashed_password")

        with patch("domain.entities.user.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            user.update_password("new_hashed_password")

            assert user.hashed_password == "new_hashed_password"
            assert user.updated_at == mock_now

    def test_update_password_empty(self):
        """Test updating password with empty value raises error."""
        email = Email("test@example.com")
        user = User.create(email, "testuser", "hashed_password")

        with pytest.raises(ValueError, match="Hashed password cannot be empty"):
            user.update_password("")

    def test_deactivate_user(self):
        """Test deactivating user."""
        email = Email("test@example.com")
        user = User.create(email, "testuser", "hashed_password")
        assert user.is_active is True

        with patch("domain.entities.user.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            user.deactivate()

            assert user.is_active is False
            assert user.updated_at == mock_now

    def test_activate_user(self):
        """Test activating user."""
        email = Email("test@example.com")
        user = User.create(email, "testuser", "hashed_password")
        user.deactivate()
        assert user.is_active is False

        with patch("domain.entities.user.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            user.activate()

            assert user.is_active is True
            assert user.updated_at == mock_now


class TestTask:
    """Tests for Task entity."""

    def test_create_task(self):
        """Test creating a task with the create class method."""
        user_id = UserId.generate()
        title = "Test Task"
        description = "Test description"

        with patch("domain.value_objects.task_id.TaskId.generate") as mock_generate:
            mock_id = TaskId("123e4567-e89b-12d3-a456-426614174001")
            mock_generate.return_value = mock_id

            task = Task.create(user_id, title, description)

            assert task.id == mock_id
            assert task.user_id == user_id
            assert task.title == title
            assert task.description == description
            assert task.completed is False
            assert isinstance(task.created_at, datetime)
            assert task.updated_at is None

    def test_create_task_without_description(self):
        """Test creating task without description."""
        user_id = UserId.generate()
        title = "Test Task"

        task = Task.create(user_id, title)

        assert task.title == title
        assert task.description is None

    def test_create_task_empty_title(self):
        """Test creating task with empty title raises error."""
        user_id = UserId.generate()

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task.create(user_id, "")

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task.create(user_id, "   ")  # Only whitespace

    def test_create_task_title_too_long(self):
        """Test creating task with title too long raises error."""
        user_id = UserId.generate()
        long_title = "x" * 201  # 201 characters

        with pytest.raises(ValueError, match="Task title cannot exceed 200 characters"):
            Task.create(user_id, long_title)

    def test_create_task_description_too_long(self):
        """Test creating task with description too long raises error."""
        user_id = UserId.generate()
        long_description = "x" * 1001  # 1001 characters

        with pytest.raises(
            ValueError, match="Task description cannot exceed 1000 characters"
        ):
            Task.create(user_id, "Valid title", long_description)

    def test_update_title(self):
        """Test updating task title."""
        user_id = UserId.generate()
        task = Task.create(user_id, "Old Title", "Description")

        with patch("domain.entities.task.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            task.update_title("New Title")

            assert task.title == "New Title"
            assert task.updated_at == mock_now

    def test_update_title_empty(self):
        """Test updating title with empty value raises error."""
        user_id = UserId.generate()
        task = Task.create(user_id, "Original Title")

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task.update_title("")

    def test_update_description(self):
        """Test updating task description."""
        user_id = UserId.generate()
        task = Task.create(user_id, "Title", "Old description")

        with patch("domain.entities.task.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            task.update_description("New description")

            assert task.description == "New description"
            assert task.updated_at == mock_now

    def test_update_description_to_none(self):
        """Test updating description to None."""
        user_id = UserId.generate()
        task = Task.create(user_id, "Title", "Description")

        task.update_description(None)

        assert task.description is None

    def test_mark_completed(self):
        """Test marking task as completed."""
        user_id = UserId.generate()
        task = Task.create(user_id, "Title")
        assert task.completed is False

        with patch("domain.entities.task.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            task.mark_completed()

            assert task.completed is True
            assert task.updated_at == mock_now

    def test_mark_completed_already_completed(self):
        """Test marking already completed task doesn't update timestamp."""
        user_id = UserId.generate()
        task = Task.create(user_id, "Title")
        task.mark_completed()
        original_updated_at = task.updated_at

        task.mark_completed()  # Mark completed again

        assert task.completed is True
        assert task.updated_at == original_updated_at  # Should not change

    def test_mark_incomplete(self):
        """Test marking task as incomplete."""
        user_id = UserId.generate()
        task = Task.create(user_id, "Title")
        task.mark_completed()
        assert task.completed is True

        with patch("domain.entities.task.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            task.mark_incomplete()

            assert task.completed is False
            assert task.updated_at == mock_now

    def test_belongs_to_user(self):
        """Test checking if task belongs to user."""
        user_id = UserId.generate()
        other_user_id = UserId.generate()
        task = Task.create(user_id, "Title")

        assert task.belongs_to_user(user_id) is True
        assert task.belongs_to_user(other_user_id) is False
