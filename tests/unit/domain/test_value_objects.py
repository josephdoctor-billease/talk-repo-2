"""
Unit tests for domain value objects.
"""

import uuid

import pytest

from domain.value_objects.email import Email
from domain.value_objects.password import Password
from domain.value_objects.task_id import TaskId
from domain.value_objects.user_id import UserId


class TestEmail:
    """Tests for Email value object."""

    def test_valid_email_creation(self):
        """Test creating a valid email."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
            "123@456.com",
        ]

        for email_str in valid_emails:
            email = Email(email_str)
            assert email.value == email_str
            assert str(email) == email_str

    def test_invalid_email_creation(self):
        """Test creating invalid emails raises ValueError."""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "test@",
            "",
            "test space@example.com",
        ]

        for email_str in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                Email(email_str)

    def test_email_equality(self):
        """Test email equality comparison."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3
        assert email1 == "test@example.com"
        assert email1 != "other@example.com"

    def test_email_immutable(self):
        """Test that email is immutable (frozen dataclass)."""
        email = Email("test@example.com")
        with pytest.raises(Exception):  # FrozenInstanceError in Python 3.9+
            email.value = "new@example.com"  # type: ignore


class TestPassword:
    """Tests for Password value object."""

    def test_valid_password_creation(self):
        """Test creating valid passwords."""
        valid_passwords = ["Password123", "StrongP@ssw0rd", "MySecure123", "Test1234A"]

        for password_str in valid_passwords:
            password = Password(password_str)
            assert password.value == password_str

    def test_invalid_password_creation(self):
        """Test creating invalid passwords raises ValueError."""
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123",  # No uppercase
            "NOLOWERCASE123",  # No lowercase
            "NoDigitsHere",  # No digits
            "1234567",  # Only digits, too short
        ]

        for password_str in invalid_passwords:
            with pytest.raises(ValueError, match="Password must be at least"):
                Password(password_str)

    def test_password_string_representation(self):
        """Test password string representation is hidden."""
        password = Password("SecretPassword123")
        assert str(password) == "***HIDDEN***"
        assert repr(password) == "Password(***HIDDEN***)"

    def test_password_immutable(self):
        """Test that password is immutable."""
        password = Password("SecretPassword123")
        with pytest.raises(Exception):
            password.value = "NewPassword123"  # type: ignore


class TestUserId:
    """Tests for UserId value object."""

    def test_valid_user_id_creation(self):
        """Test creating valid user IDs."""
        valid_uuid = str(uuid.uuid4())
        user_id = UserId(valid_uuid)
        assert user_id.value == valid_uuid
        assert str(user_id) == valid_uuid

    def test_invalid_user_id_creation(self):
        """Test creating invalid user IDs raises ValueError."""
        invalid_uuids = ["invalid-uuid", "123-456-789", "", "not-a-uuid-at-all"]

        for invalid_uuid in invalid_uuids:
            with pytest.raises(ValueError, match="Invalid UUID format"):
                UserId(invalid_uuid)

    def test_generate_user_id(self):
        """Test generating new user ID."""
        user_id = UserId.generate()
        assert user_id.value
        assert len(user_id.value) == 36  # Standard UUID string length

        # Should generate unique IDs
        user_id2 = UserId.generate()
        assert user_id != user_id2

    def test_user_id_equality(self):
        """Test user ID equality comparison."""
        uuid_str = str(uuid.uuid4())
        user_id1 = UserId(uuid_str)
        user_id2 = UserId(uuid_str)
        user_id3 = UserId.generate()

        assert user_id1 == user_id2
        assert user_id1 != user_id3
        assert user_id1 == uuid_str
        assert user_id1 != str(user_id3.value)


class TestTaskId:
    """Tests for TaskId value object."""

    def test_valid_task_id_creation(self):
        """Test creating valid task IDs."""
        valid_uuid = str(uuid.uuid4())
        task_id = TaskId(valid_uuid)
        assert task_id.value == valid_uuid
        assert str(task_id) == valid_uuid

    def test_invalid_task_id_creation(self):
        """Test creating invalid task IDs raises ValueError."""
        invalid_uuids = ["invalid-uuid", "123-456-789", "", "not-a-uuid"]

        for invalid_uuid in invalid_uuids:
            with pytest.raises(ValueError, match="Invalid UUID format"):
                TaskId(invalid_uuid)

    def test_generate_task_id(self):
        """Test generating new task ID."""
        task_id = TaskId.generate()
        assert task_id.value
        assert len(task_id.value) == 36

        # Should generate unique IDs
        task_id2 = TaskId.generate()
        assert task_id != task_id2

    def test_task_id_equality(self):
        """Test task ID equality comparison."""
        uuid_str = str(uuid.uuid4())
        task_id1 = TaskId(uuid_str)
        task_id2 = TaskId(uuid_str)
        task_id3 = TaskId.generate()

        assert task_id1 == task_id2
        assert task_id1 != task_id3
        assert task_id1 == uuid_str
        assert task_id1 != str(task_id3.value)
