import os


class DatabaseConfig:  # pragma: no cover
    def __init__(self):
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://test_user:test_password@localhost:5433/task_management_test",
        )
        self.echo: bool = os.getenv("DATABASE_ECHO", "true").lower() == "true"
        self.pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
        self.pool_timeout: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
        self.pool_recycle: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

    @property
    def sqlalchemy_database_url(self) -> str:
        return self.database_url

    def get_sync_database_url(self) -> str:
        # For Alembic, we need a synchronous driver
        return self.database_url.replace("+asyncpg", "+psycopg2")


database_config = DatabaseConfig()
