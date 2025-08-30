from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config.auth import auth_config
from infrastructure.database.base import create_tables
from presentation.api.auth_router import router as auth_router
from presentation.api.task_router import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    # Startup - only create tables if not in test mode
    if not os.getenv("TESTING"):
        await create_tables()
    yield
    # Shutdown


app = FastAPI(
    title="Task Management API",
    description="A DDD-based REST API for managing tasks with authentication",
    version="2.0.0",
    lifespan=lifespan,
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


@app.get("/", summary="Root endpoint")
async def root():
    return {
        "message": "Welcome to Task Management API v2.0",
        "docs": "/docs",
        "version": "2.0.0",
        "features": [
            "User authentication with JWT",
            "Domain-driven design architecture",
            "PostgreSQL database with migrations",
            "User-specific task management",
            "RESTful API endpoints",
        ],
    }


@app.get("/health", summary="Health check")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port="8000", reload=True)
