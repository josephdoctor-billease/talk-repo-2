"""
Pytest configuration and fixtures for the task management API.
"""

import os
import asyncio
from typing import AsyncGenerator, Generator

# Set testing environment variable BEFORE any other imports
os.environ["TESTING"] = "true"

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Test database URL - ensure it's different from main app database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@localhost:5433/task_management_test",
)

# Wait for database to be ready
import time
import asyncpg


async def wait_for_db(database_url: str, max_retries: int = 30) -> bool:
    """Wait for database to be ready with connection retries."""
    for attempt in range(max_retries):
        try:
            # Parse connection string for asyncpg
            db_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            conn = await asyncpg.connect(db_url)
            await conn.close()
            return True
        except (asyncpg.PostgresError, OSError, ConnectionRefusedError):
            if attempt < max_retries - 1:
                time.sleep(1)
            continue
    return False


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create a test database engine for each test."""
    # Wait for database to be ready
    db_ready = await wait_for_db(TEST_DATABASE_URL)
    if not db_ready:
        pytest.skip("Test database is not available")

    engine = create_async_engine(
        TEST_DATABASE_URL, 
        echo=False, 
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=3600
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """Create test database tables."""
    # Import here to avoid circular imports
    from infrastructure.database.base import Base
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def db_session(test_engine, test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_app() -> FastAPI:
    """Create a test FastAPI application."""
    # Create a completely separate test app to avoid database conflicts
    from fastapi.middleware.cors import CORSMiddleware
    from infrastructure.config.auth import auth_config
    from presentation.api.auth_router import router as auth_router
    from presentation.api.task_router import router as task_router
    
    app = FastAPI(
        title="Task Management API - Test",
        description="A DDD-based REST API for managing tasks with authentication - Test Version",
        version="2.0.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=auth_config.cors_origins,
        allow_credentials=auth_config.cors_allow_credentials,
        allow_methods=auth_config.cors_allow_methods,
        allow_headers=auth_config.cors_allow_headers,
    )
    
    # Include routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(task_router, prefix="/api/v1")
    
    return app


@pytest.fixture
async def client(test_app: FastAPI, test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an HTTP client for testing API endpoints."""
    from httpx import ASGITransport
    from infrastructure.database.base import get_session

    # Create a sessionmaker
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        """Get a database session for testing."""
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    test_app.dependency_overrides[get_session] = get_test_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            yield ac
    finally:
        # Clean up dependency override
        test_app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
) -> AsyncGenerator[tuple[AsyncClient, dict], None]:
    """Create an authenticated HTTP client with a test user."""
    # Create unique credentials for this test session
    import time
    import random
    unique_suffix = f"{int(time.time())}{random.randint(1000, 9999)}"
    
    # First, create a user via the API
    signup_response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": f"testuser{unique_suffix}@example.com",
            "username": f"testuser{unique_suffix}", 
            "password": "TestPassword123"
        },
    )
    
    assert signup_response.status_code == 201

    signup_data = signup_response.json()
    access_token = signup_data["tokens"]["access_token"]

    # Set authorization header
    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client, {
        "user": signup_data["user"],
        "access_token": access_token,
        "refresh_token": signup_data["tokens"]["refresh_token"],
    }


# Test data factories using Faker
@pytest.fixture
def user_factory():
    """Factory for creating test user data."""
    from faker import Faker
    import time
    import random

    fake = Faker()

    def _create_user_data(**kwargs):
        # Add timestamp and random component to ensure uniqueness across test runs
        unique_suffix = f"{int(time.time())}{random.randint(1000, 9999)}"
        defaults = {
            "email": f"user{unique_suffix}@example.com",
            "username": f"user{unique_suffix}",
            "password": "TestPassword123",
        }
        defaults.update(kwargs)
        return defaults

    return _create_user_data


@pytest.fixture
def task_factory():
    """Factory for creating test task data."""
    from faker import Faker

    fake = Faker()

    def _create_task_data(**kwargs):
        defaults = {
            "title": fake.sentence(nb_words=4)[:-1],  # Remove the period
            "description": fake.text(max_nb_chars=200),
            "completed": False,
        }
        defaults.update(kwargs)
        return defaults

    return _create_task_data


# Mark all tests as asyncio by default
pytest_plugins = ("pytest_asyncio",)
