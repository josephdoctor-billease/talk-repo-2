"""
Unit tests for application use cases.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from application.dto.user_dto import UserCreateDTO, UserLoginDTO
from application.use_cases.auth_use_cases import AuthUseCases
from domain.entities.user import User
from domain.value_objects.email import Email
from domain.value_objects.password import Password
from domain.value_objects.user_id import UserId


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_password_service():
    """Mock password service."""
    mock = Mock()
    mock.hash_password.return_value = "hashed_password"
    mock.verify_password.return_value = True
    return mock


@pytest.fixture
def mock_jwt_service():
    """Mock JWT service."""
    mock = Mock()
    mock.create_access_token.return_value = "access_token"
    mock.create_refresh_token.return_value = "refresh_token"
    mock.access_token_expire_minutes = 30
    mock.verify_token.return_value = {"sub": "user_id", "username": "testuser"}
    return mock


@pytest.fixture
def auth_use_cases(mock_user_repository, mock_password_service, mock_jwt_service):
    """Auth use cases with mocked dependencies."""
    return AuthUseCases(mock_user_repository, mock_password_service, mock_jwt_service)


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    email = Email("test@example.com")
    user = User.create(email, "testuser", "hashed_password")
    return user


class TestAuthUseCases:
    """Tests for AuthUseCases."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, auth_use_cases, mock_user_repository, sample_user
    ):
        """Test successful user registration."""
        # Setup
        user_data = UserCreateDTO(
            email="test@example.com", username="testuser", password="TestPassword123"
        )

        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.create.return_value = sample_user

        # Execute
        result = await auth_use_cases.register_user(user_data)

        # Verify
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["username"] == "testuser"
        assert result["tokens"].access_token == "access_token"
        assert result["tokens"].refresh_token == "refresh_token"

        # Verify repository calls
        mock_user_repository.exists_by_email.assert_called_once()
        mock_user_repository.exists_by_username.assert_called_once()
        mock_user_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(
        self, auth_use_cases, mock_user_repository
    ):
        """Test user registration with existing email."""
        user_data = UserCreateDTO(
            email="test@example.com", username="testuser", password="TestPassword123"
        )

        mock_user_repository.exists_by_email.return_value = True

        with pytest.raises(ValueError, match="User with this email already exists"):
            await auth_use_cases.register_user(user_data)

    @pytest.mark.asyncio
    async def test_register_user_username_exists(
        self, auth_use_cases, mock_user_repository
    ):
        """Test user registration with existing username."""
        user_data = UserCreateDTO(
            email="test@example.com", username="testuser", password="TestPassword123"
        )

        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = True

        with pytest.raises(ValueError, match="User with this username already exists"):
            await auth_use_cases.register_user(user_data)

    @pytest.mark.asyncio
    async def test_register_user_invalid_password(
        self, auth_use_cases, mock_user_repository
    ):
        """Test user registration with invalid password."""
        user_data = UserCreateDTO(
            email="test@example.com",
            username="testuser",
            password="weakpass123",  # Has minimum length but no uppercase
        )

        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = False

        with pytest.raises(ValueError, match="Password must be at least"):
            await auth_use_cases.register_user(user_data)

    @pytest.mark.asyncio
    async def test_login_user_success(
        self, auth_use_cases, mock_user_repository, sample_user
    ):
        """Test successful user login."""
        login_data = UserLoginDTO(email="test@example.com", password="TestPassword123")

        mock_user_repository.get_by_email.return_value = sample_user

        result = await auth_use_cases.login_user(login_data)

        assert result["user"]["email"] == "test@example.com"
        assert result["tokens"].access_token == "access_token"
        assert result["tokens"].refresh_token == "refresh_token"

        mock_user_repository.get_by_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_use_cases, mock_user_repository):
        """Test login with non-existent user."""
        login_data = UserLoginDTO(
            email="nonexistent@example.com", password="TestPassword123"
        )

        mock_user_repository.get_by_email.return_value = None

        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_use_cases.login_user(login_data)

    @pytest.mark.asyncio
    async def test_login_user_inactive(
        self, auth_use_cases, mock_user_repository, sample_user
    ):
        """Test login with inactive user."""
        login_data = UserLoginDTO(email="test@example.com", password="TestPassword123")

        sample_user.deactivate()
        mock_user_repository.get_by_email.return_value = sample_user

        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_use_cases.login_user(login_data)

    @pytest.mark.asyncio
    async def test_login_user_wrong_password(
        self, auth_use_cases, mock_user_repository, mock_password_service, sample_user
    ):
        """Test login with wrong password."""
        login_data = UserLoginDTO(email="test@example.com", password="WrongPassword123")

        mock_user_repository.get_by_email.return_value = sample_user
        mock_password_service.verify_password.return_value = False

        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_use_cases.login_user(login_data)

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self, auth_use_cases, mock_user_repository, mock_jwt_service, sample_user
    ):
        """Test successful token refresh."""
        refresh_token = "valid_refresh_token"

        mock_jwt_service.verify_token.return_value = {"sub": str(sample_user.id)}
        mock_user_repository.get_by_id.return_value = sample_user
        mock_jwt_service.create_access_token.return_value = "new_access_token"

        result = await auth_use_cases.refresh_token(refresh_token)

        assert result.access_token == "new_access_token"
        assert result.refresh_token == refresh_token  # Same refresh token

        mock_jwt_service.verify_token.assert_called_once_with(refresh_token, "refresh")
        mock_user_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, auth_use_cases, mock_jwt_service):
        """Test token refresh with invalid token."""
        refresh_token = "invalid_refresh_token"

        mock_jwt_service.verify_token.return_value = None

        with pytest.raises(ValueError, match="Invalid refresh token"):
            await auth_use_cases.refresh_token(refresh_token)

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(
        self, auth_use_cases, mock_user_repository, mock_jwt_service
    ):
        """Test token refresh with user not found."""
        refresh_token = "valid_refresh_token"

        mock_jwt_service.verify_token.return_value = {
            "sub": "550e8400-e29b-41d4-a716-446655440000"
        }
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Invalid refresh token"):
            await auth_use_cases.refresh_token(refresh_token)

    @pytest.mark.asyncio
    async def test_get_current_user(
        self, auth_use_cases, mock_user_repository, sample_user
    ):
        """Test getting current user."""
        mock_user_repository.get_by_id.return_value = sample_user

        result = await auth_use_cases.get_current_user(sample_user.id)

        assert result == sample_user
        mock_user_repository.get_by_id.assert_called_once_with(sample_user.id)

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(
        self, auth_use_cases, mock_user_repository
    ):
        """Test getting current user when not found."""
        user_id = UserId.generate()
        mock_user_repository.get_by_id.return_value = None

        result = await auth_use_cases.get_current_user(user_id)

        assert result is None
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
