"""
Unit tests for infrastructure authentication services.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from domain.value_objects.password import Password
from domain.value_objects.user_id import UserId
from infrastructure.auth.jwt_service import JWTService
from infrastructure.auth.password_service import PasswordService


class TestPasswordService:
    """Tests for PasswordService."""

    def setup_method(self):
        """Setup method called before each test."""
        self.password_service = PasswordService()

    def test_hash_password(self):
        """Test password hashing."""
        password = Password("TestPassword123")
        hashed = self.password_service.hash_password(password)

        assert hashed != password.value
        assert isinstance(hashed, str)
        assert len(hashed) > 50  # bcrypt hash is typically longer
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_hash_password_different_results(self):
        """Test that hashing the same password produces different results (salt)."""
        password = Password("TestPassword123")
        hash1 = self.password_service.hash_password(password)
        hash2 = self.password_service.hash_password(password)

        assert hash1 != hash2  # Different due to salt

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = Password("TestPassword123")
        hashed = self.password_service.hash_password(password)

        result = self.password_service.verify_password("TestPassword123", hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = Password("TestPassword123")
        hashed = self.password_service.hash_password(password)

        result = self.password_service.verify_password("WrongPassword", hashed)
        assert result is False

    def test_verify_password_empty(self):
        """Test password verification with empty password."""
        password = Password("TestPassword123")
        hashed = self.password_service.hash_password(password)

        result = self.password_service.verify_password("", hashed)
        assert result is False

    def test_needs_update(self):
        """Test checking if password hash needs update."""
        password = Password("TestPassword123")
        hashed = self.password_service.hash_password(password)

        # Fresh hash should not need update
        result = self.password_service.needs_update(hashed)
        assert result is False


class TestJWTService:
    """Tests for JWTService."""

    def setup_method(self):
        """Setup method called before each test."""
        with patch.dict(
            "os.environ",
            {
                "JWT_SECRET_KEY": "test-secret-key",
                "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
                "REFRESH_TOKEN_EXPIRE_DAYS": "7",
            },
        ):
            self.jwt_service = JWTService()

    def test_create_access_token(self):
        """Test creating access token."""
        user_id = UserId.generate()
        username = "testuser"

        token = self.jwt_service.create_access_token(user_id, username)

        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are typically long
        assert "." in token  # JWT has dots separating header, payload, signature

    def test_create_refresh_token(self):
        """Test creating refresh token."""
        user_id = UserId.generate()

        token = self.jwt_service.create_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 100
        assert "." in token

    def test_verify_access_token_valid(self):
        """Test verifying valid access token."""
        user_id = UserId.generate()
        username = "testuser"

        token = self.jwt_service.create_access_token(user_id, username)
        payload = self.jwt_service.verify_token(token, "access")

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["username"] == username
        assert payload["type"] == "access"

    def test_verify_refresh_token_valid(self):
        """Test verifying valid refresh token."""
        user_id = UserId.generate()

        token = self.jwt_service.create_refresh_token(user_id)
        payload = self.jwt_service.verify_token(token, "refresh")

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_verify_token_invalid(self):
        """Test verifying invalid token."""
        invalid_token = "invalid.token.here"

        payload = self.jwt_service.verify_token(invalid_token)

        assert payload is None

    def test_verify_token_wrong_type(self):
        """Test verifying token with wrong type."""
        user_id = UserId.generate()
        access_token = self.jwt_service.create_access_token(user_id, "testuser")

        # Try to verify access token as refresh token
        payload = self.jwt_service.verify_token(access_token, "refresh")

        assert payload is None

    def test_get_user_id_from_token_valid(self):
        """Test extracting user ID from valid token."""
        user_id = UserId.generate()
        token = self.jwt_service.create_access_token(user_id, "testuser")

        extracted_id = self.jwt_service.get_user_id_from_token(token)

        assert extracted_id == user_id

    def test_get_user_id_from_token_invalid(self):
        """Test extracting user ID from invalid token."""
        invalid_token = "invalid.token.here"

        extracted_id = self.jwt_service.get_user_id_from_token(invalid_token)

        assert extracted_id is None

    def test_refresh_access_token_valid(self):
        """Test refreshing access token with valid refresh token."""
        user_id = UserId.generate()
        refresh_token = self.jwt_service.create_refresh_token(user_id)

        new_access_token = self.jwt_service.refresh_access_token(refresh_token)

        assert new_access_token is not None
        assert isinstance(new_access_token, str)

        # Verify the new access token
        payload = self.jwt_service.verify_token(new_access_token, "access")
        assert payload is not None
        assert payload["sub"] == str(user_id)

    def test_refresh_access_token_invalid(self):
        """Test refreshing access token with invalid refresh token."""
        invalid_refresh_token = "invalid.refresh.token"

        new_access_token = self.jwt_service.refresh_access_token(invalid_refresh_token)

        assert new_access_token is None

    @patch("infrastructure.auth.jwt_service.datetime")
    def test_token_expiration(self, mock_datetime):
        """Test token expiration handling."""
        # Mock current time
        now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = now

        user_id = UserId.generate()
        token = self.jwt_service.create_access_token(user_id, "testuser")

        # Mock time after expiration
        expired_time = now + timedelta(minutes=31)  # Past 30 minute expiry
        mock_datetime.now.return_value = expired_time

        payload = self.jwt_service.verify_token(token, "access")

        # Token should be expired and return None
        assert payload is None

    def test_token_contains_expected_claims(self):
        """Test that tokens contain expected claims."""
        user_id = UserId.generate()
        username = "testuser"

        access_token = self.jwt_service.create_access_token(user_id, username)
        refresh_token = self.jwt_service.create_refresh_token(user_id)

        access_payload = self.jwt_service.verify_token(access_token, "access")
        refresh_payload = self.jwt_service.verify_token(refresh_token, "refresh")

        # Check access token claims
        assert "sub" in access_payload
        assert "username" in access_payload
        assert "exp" in access_payload
        assert "type" in access_payload
        assert access_payload["type"] == "access"

        # Check refresh token claims
        assert "sub" in refresh_payload
        assert "exp" in refresh_payload
        assert "type" in refresh_payload
        assert refresh_payload["type"] == "refresh"
        assert "username" not in refresh_payload  # Refresh tokens don't need username
