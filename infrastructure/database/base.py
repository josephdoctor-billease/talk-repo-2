import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Get database URL with fallback to test database if TESTING is set."""
    if os.getenv("TESTING"):
        return os.getenv(
            "TEST_DATABASE_URL",
            "postgresql+asyncpg://test_user:test_password@localhost:5433/task_management_test",
        )
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://test_user:test_password@localhost:5433/task_management_test",
    )

DATABASE_URL = get_database_url()

Base = declarative_base()

engine = create_async_engine(
    DATABASE_URL, echo=True, future=True  # Set to False in production
)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():  # pragma: no cover
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():  # pragma: no cover
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
