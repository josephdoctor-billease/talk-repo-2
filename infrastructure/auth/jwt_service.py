import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from domain.value_objects.user_id import UserId


class JWTService:
    def __init__(self):
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY", "your-secret-key-change-this-in-production"
        )
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_token_expire_days = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

    def create_access_token(self, user_id: UserId, username: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "username": username,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: UserId) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None

    def get_user_id_from_token(self, token: str) -> Optional[UserId]:
        payload = self.verify_token(token)
        if payload:
            user_id_str = payload.get("sub")
            if user_id_str:
                try:
                    return UserId(user_id_str)
                except ValueError:
                    return None
        return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload = self.verify_token(refresh_token, "refresh")
        if payload:
            user_id_str = payload.get("sub")
            if user_id_str:
                try:
                    user_id = UserId(user_id_str)
                    return self.create_access_token(user_id, "")
                except ValueError:
                    return None
        return None


jwt_service = JWTService()
