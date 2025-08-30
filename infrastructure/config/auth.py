import os
from typing import List


class AuthConfig:  # pragma: no cover
    def __init__(self):
        self.jwt_secret_key: str = os.getenv(
            "JWT_SECRET_KEY", "your-secret-key-change-this-in-production"
        )
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_token_expire_days: int = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

        # CORS settings
        self.cors_origins: List[str] = self._parse_cors_origins()
        self.cors_allow_credentials: bool = (
            os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        )
        self.cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.cors_allow_headers: List[str] = ["*"]

    def _parse_cors_origins(self) -> List[str]:
        origins_str = os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        )
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


auth_config = AuthConfig()
