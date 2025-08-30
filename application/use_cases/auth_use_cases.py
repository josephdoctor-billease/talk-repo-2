from typing import Any, Dict, Optional

from application.dto.user_dto import TokenResponseDTO, UserCreateDTO, UserLoginDTO
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.password import Password
from domain.value_objects.user_id import UserId
from infrastructure.auth.jwt_service import JWTService
from infrastructure.auth.password_service import PasswordService


class AuthUseCases:
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: JWTService,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def register_user(self, user_data: UserCreateDTO) -> Dict[str, Any]:
        """Register a new user"""
        # Check if user already exists
        email = Email(user_data.email)
        if await self.user_repository.exists_by_email(email):
            raise ValueError("User with this email already exists")

        if await self.user_repository.exists_by_username(user_data.username):
            raise ValueError("User with this username already exists")

        # Validate password and create user
        password = Password(user_data.password)
        hashed_password = self.password_service.hash_password(password)

        user = User.create(
            email=email, username=user_data.username, hashed_password=hashed_password
        )

        # Save user to repository
        created_user = await self.user_repository.create(user)

        # Generate tokens
        access_token = self.jwt_service.create_access_token(
            created_user.id, created_user.username
        )
        refresh_token = self.jwt_service.create_refresh_token(created_user.id)

        return {
            "user": {
                "id": str(created_user.id),
                "email": str(created_user.email),
                "username": created_user.username,
                "is_active": created_user.is_active,
                "created_at": created_user.created_at,
                "updated_at": created_user.updated_at,
            },
            "tokens": TokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.jwt_service.access_token_expire_minutes * 60,
            ),
        }

    async def login_user(self, login_data: UserLoginDTO) -> Dict[str, Any]:
        """Login user and return tokens"""
        email = Email(login_data.email)
        user = await self.user_repository.get_by_email(email)

        if not user or not user.is_active:
            raise ValueError("Invalid email or password")

        if not self.password_service.verify_password(
            login_data.password, user.hashed_password
        ):
            raise ValueError("Invalid email or password")

        # Generate tokens
        access_token = self.jwt_service.create_access_token(user.id, user.username)
        refresh_token = self.jwt_service.create_refresh_token(user.id)

        return {
            "user": {
                "id": str(user.id),
                "email": str(user.email),
                "username": user.username,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            },
            "tokens": TokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.jwt_service.access_token_expire_minutes * 60,
            ),
        }

    async def refresh_token(self, refresh_token: str) -> TokenResponseDTO:
        """Refresh access token using refresh token"""
        payload = self.jwt_service.verify_token(refresh_token, "refresh")
        if not payload:
            raise ValueError("Invalid refresh token")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Invalid refresh token payload")

        try:
            user_id = UserId(user_id_str)
            user = await self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")

            # Generate new access token
            access_token = self.jwt_service.create_access_token(user.id, user.username)

            return TokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,  # Keep the same refresh token
                expires_in=self.jwt_service.access_token_expire_minutes * 60,
            )
        except ValueError:
            raise ValueError("Invalid refresh token")

    async def get_current_user(self, user_id: UserId) -> Optional[User]:
        """Get current user by ID"""
        return await self.user_repository.get_by_id(user_id)
