"""
Integration tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Integration tests for authentication API endpoints."""

    @pytest.mark.integration
    async def test_signup_success(self, client: AsyncClient, user_factory):
        """Test successful user signup."""
        # Use factory defaults with unique values to avoid conflicts
        user_data = user_factory(
            password="SecurePassword123",
        )

        response = await client.post("/api/v1/auth/signup", json=user_data)

        assert response.status_code == 201
        data = response.json()

        assert data["message"] == "User registered successfully"
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["is_active"] is True
        assert "id" in data["user"]
        assert "created_at" in data["user"]

        # Check tokens
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
        assert data["tokens"]["token_type"] == "bearer"
        assert data["tokens"]["expires_in"] == 1800  # 30 minutes

    @pytest.mark.integration
    async def test_signup_invalid_email(self, client: AsyncClient, user_factory):
        """Test signup with invalid email."""
        user_data = user_factory(email="invalid-email")

        response = await client.post("/api/v1/auth/signup", json=user_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    async def test_signup_weak_password(self, client: AsyncClient, user_factory):
        """Test signup with weak password."""
        user_data = user_factory(password="weak")

        response = await client.post("/api/v1/auth/signup", json=user_data)

        assert response.status_code == 422  # FastAPI validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    async def test_signup_duplicate_email(self, client: AsyncClient, user_factory):
        """Test signup with duplicate email."""
        # Use a unique email for this specific test with extra uniqueness
        import time
        import random
        unique_id = f"{int(time.time())}{random.randint(10000, 99999)}"
        unique_email = f"duplicate{unique_id}@example.com"
        
        user_data = user_factory(email=unique_email, username=f"user{unique_id}")

        # First signup
        response1 = await client.post("/api/v1/auth/signup", json=user_data)
        assert response1.status_code == 201

        # Second signup with same email but different username
        user_data2 = user_factory(email=unique_email, username=f"different{unique_id}")
        response2 = await client.post("/api/v1/auth/signup", json=user_data2)

        assert response2.status_code == 400
        data = response2.json()
        assert "email already exists" in data["detail"]

    @pytest.mark.integration
    async def test_signup_duplicate_username(self, client: AsyncClient, user_factory):
        """Test signup with duplicate username."""
        # Use a unique username for this specific test
        import time
        unique_username = f"duplicate_user{int(time.time())}"
        
        user_data = user_factory(username=unique_username)

        # First signup
        response1 = await client.post("/api/v1/auth/signup", json=user_data)
        assert response1.status_code == 201

        # Second signup with same username
        user_data2 = user_factory(
            email=f"different{int(time.time())}@example.com", username=unique_username
        )
        response2 = await client.post("/api/v1/auth/signup", json=user_data2)

        assert response2.status_code == 400
        data = response2.json()
        assert "username already exists" in data["detail"]

    @pytest.mark.integration
    async def test_login_success(self, client: AsyncClient, user_factory):
        """Test successful user login."""
        # First create a user with unique credentials
        import time
        unique_suffix = int(time.time())
        user_data = user_factory(
            email=f"logintest{unique_suffix}@example.com",
            username=f"loginuser{unique_suffix}",
            password="LoginPassword123",
        )
        signup_response = await client.post("/api/v1/auth/signup", json=user_data)
        assert signup_response.status_code == 201

        # Then login
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Login successful"
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]

    @pytest.mark.integration
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with non-existent email."""
        login_data = {"email": "nonexistent@example.com", "password": "Password123"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid email or password"

    @pytest.mark.integration
    async def test_login_wrong_password(self, client: AsyncClient, user_factory):
        """Test login with wrong password."""
        # Create a user
        user_data = user_factory()
        signup_response = await client.post("/api/v1/auth/signup", json=user_data)
        assert signup_response.status_code == 201

        # Try to login with wrong password
        login_data = {"email": user_data["email"], "password": "WrongPassword123"}
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid email or password"

    @pytest.mark.integration
    async def test_get_current_user(self, authenticated_client):
        """Test getting current user information."""
        client, auth_data = authenticated_client

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()

        # Use the actual email from the fixture instead of hardcoded value
        assert data["email"] == auth_data["user"]["email"]
        assert data["username"] == auth_data["user"]["username"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.integration
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.integration
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        client.headers.update({"Authorization": "Bearer invalid_token"})

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid authentication credentials"

    @pytest.mark.integration
    async def test_refresh_token_success(self, client: AsyncClient, user_factory):
        """Test successful token refresh."""
        # Create user and login
        user_data = user_factory()
        signup_response = await client.post("/api/v1/auth/signup", json=user_data)
        signup_data = signup_response.json()

        refresh_token = signup_data["tokens"]["refresh_token"]

        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800

        # New access token should be different (or same if created within same second)
        # The important thing is that refresh_token returns a valid response
        assert data["access_token"] is not None
        # Refresh token should be the same
        assert data["refresh_token"] == refresh_token

    @pytest.mark.integration
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid refresh token."""
        refresh_data = {"refresh_token": "invalid_refresh_token"}

        response = await client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid refresh token"

    @pytest.mark.integration
    async def test_logout(self, client: AsyncClient):
        """Test user logout."""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert "Logout successful" in data["message"]

    @pytest.mark.integration
    async def test_auth_flow_complete(self, client: AsyncClient, user_factory):
        """Test complete authentication flow: signup -> login -> get user -> refresh -> logout."""
        # 1. Signup - use user_factory to generate unique values
        user_data = user_factory()
        signup_response = await client.post("/api/v1/auth/signup", json=user_data)
        assert signup_response.status_code == 201
        signup_data = signup_response.json()

        # 2. Login
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        login_data_response = login_response.json()

        # 3. Get current user
        access_token = login_data_response["tokens"]["access_token"]
        client.headers.update({"Authorization": f"Bearer {access_token}"})

        me_response = await client.get("/api/v1/auth/me")
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == user_data["email"]

        # 4. Refresh token
        refresh_data = {"refresh_token": login_data_response["tokens"]["refresh_token"]}
        refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200

        # 5. Logout
        logout_response = await client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 200
