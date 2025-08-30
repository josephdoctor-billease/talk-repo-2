from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")


class UserLoginDTO(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class UserResponseDTO(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="User update timestamp")


class TokenResponseDTO(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenRefreshDTO(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")
