from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from infrastructure.auth.jwt_service import jwt_service
from infrastructure.database.base import get_session
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(  # pragma: no cover
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """Get current user from JWT token (optional - returns None if not authenticated)"""
    if not credentials:
        return None

    try:
        user_id = jwt_service.get_user_id_from_token(credentials.credentials)
        if not user_id:
            return None

        user_repository = UserRepositoryImpl(session)
        user = await user_repository.get_by_id(user_id)

        if not user or not user.is_active:
            return None

        return user
    except Exception:
        return None


async def get_current_user(  # pragma: no cover
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get current user from JWT token (required - raises exception if not authenticated)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = jwt_service.get_user_id_from_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repository = UserRepositoryImpl(session)
    user = await user_repository.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(  # pragma: no cover
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (convenience dependency)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
