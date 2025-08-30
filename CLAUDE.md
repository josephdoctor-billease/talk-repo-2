# Task Management API - Claude Code Project Documentation

## Project Overview
This is a Domain-Driven Design (DDD) based Task Management API built with FastAPI, featuring user authentication, task management, and comprehensive testing infrastructure.

## Architecture
- **Domain-Driven Design (DDD)** architecture with clear separation of concerns
- **FastAPI** web framework for REST API endpoints
- **PostgreSQL** database with async SQLAlchemy ORM
- **JWT token-based authentication** with refresh tokens
- **Alembic** database migrations
- **Docker Compose** for local development database

## Technology Stack
- **Python 3.8-3.13.1** (currently using 3.13.1)
- **FastAPI 0.104.1+** - Web framework
- **SQLAlchemy 2.0+** - ORM with async support
- **PostgreSQL** - Database
- **AsyncPG** - Async PostgreSQL driver
- **Alembic** - Database migrations
- **JWT (python-jose)** - Authentication tokens
- **bcrypt (passlib)** - Password hashing
- **pytest** - Testing framework
- **Docker & Docker Compose** - Containerization

## Project Structure
```
├── domain/                 # Domain layer - business logic
│   ├── entities/          # Domain entities (User, Task)
│   ├── value_objects/     # Value objects (Email, Password, IDs)
│   └── repositories/      # Repository interfaces
├── application/           # Application layer - use cases
│   ├── use_cases/        # Business use cases
│   └── dto/              # Data transfer objects
├── infrastructure/        # Infrastructure layer
│   ├── repositories/     # Repository implementations
│   ├── auth/            # Authentication services
│   ├── database/        # Database models and configuration
│   └── config/          # Configuration classes
├── presentation/          # Presentation layer
│   ├── api/             # FastAPI routers
│   ├── middleware/      # Authentication middleware
│   └── schemas/         # API schemas
├── tests/                # Test suite
│   ├── unit/           # Unit tests (68 tests)
│   └── integration/    # Integration tests
├── alembic/            # Database migrations
└── docker-compose.test.yml  # Test database setup
```

## Key Features
- **User Management**: Registration, login, JWT authentication
- **Task Management**: CRUD operations with user ownership
- **Database Migrations**: Alembic for schema versioning
- **Comprehensive Testing**: Unit and integration tests
- **Code Quality**: Pre-commit hooks, linting, formatting
- **Development Tools**: Tox automation, Makefile workflows

## Development Setup

### Prerequisites
- Python 3.8-3.13.1
- Docker & Docker Compose
- uv (Python package manager)

### Quick Start
```bash
# Install dependencies
uv sync --dev

# Start test database
docker-compose -f docker-compose.test.yml up -d

# Run database migrations
uv run alembic upgrade head

# Start the application
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest

# Generate coverage report
uv run pytest --cov-report=html
```

## Testing Infrastructure
- **68 Unit Tests** covering domain, application, and infrastructure layers
- **Integration Tests** for API endpoints
- **Coverage Target**: 85% (currently ~68% with pragma exclusions)
- **HTML Coverage Reports** in `htmlcov/` directory
- **Tox Automation** for multi-environment testing
- **Pre-commit Hooks** for code quality

### Test Commands
```bash
make test              # Full test suite with Docker
make test-unit         # Unit tests only
make test-integration  # Integration tests with database
make coverage          # Generate HTML coverage reports
make ci               # Full CI pipeline locally
```

## Database Configuration
- **Test Database**: PostgreSQL on port 5433
- **Connection URL**: `postgresql+asyncpg://test_user:test_password@localhost:5433/task_management_test`
- **Migrations**: Located in `alembic/versions/`
- **Models**: SQLAlchemy models in `infrastructure/database/models.py`

## Authentication Flow
1. **Registration**: POST `/api/v1/auth/signup`
2. **Login**: POST `/api/v1/auth/login` (returns access + refresh tokens)
3. **Token Refresh**: POST `/api/v1/auth/refresh`
4. **Protected Routes**: Include `Authorization: Bearer <token>` header
5. **Logout**: POST `/api/v1/auth/logout`

## Task Management
- **Create Task**: POST `/api/v1/tasks/`
- **List Tasks**: GET `/api/v1/tasks/` (user-specific, with pagination)
- **Get Task**: GET `/api/v1/tasks/{task_id}`
- **Update Task**: PUT `/api/v1/tasks/{task_id}`
- **Delete Task**: DELETE `/api/v1/tasks/{task_id}`

## Development Workflow
1. **Code Changes**: Make changes in appropriate layer
2. **Run Tests**: `make test-unit` for quick feedback
3. **Code Quality**: Pre-commit hooks run automatically
4. **Integration**: `make test-integration` with database
5. **Coverage**: `make coverage` to check test coverage
6. **CI Pipeline**: `make ci` runs full validation

## Common Commands
```bash
# Development
uv run uvicorn main:app --reload    # Start dev server
uv run pytest tests/unit           # Unit tests
uv run pytest tests/integration    # Integration tests

# Database
uv run alembic revision --autogenerate -m "Description"  # Create migration
uv run alembic upgrade head                               # Apply migrations

# Code Quality
uv run black .                     # Format code
uv run isort .                     # Sort imports
uv run flake8 .                    # Lint code
uv run mypy .                      # Type checking
uv run bandit -r .                 # Security scan

# Docker
docker-compose -f docker-compose.test.yml up -d    # Start test DB
docker-compose -f docker-compose.test.yml down     # Stop test DB
```

## Environment Variables
```bash
DATABASE_URL=postgresql+asyncpg://test_user:test_password@localhost:5433/task_management_test
JWT_SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Recent Updates
- Enhanced test coverage with pragma exclusions for runtime-only code
- Updated tox.ini to support Python 3.13.1
- Added comprehensive Makefile for development workflows
- Fixed database session management for proper transaction handling
- Implemented comprehensive testing infrastructure

## Next Steps
- Achieve 85%+ test coverage
- Add API documentation with OpenAPI/Swagger
- Implement rate limiting
- Add logging and monitoring
- Deploy with container orchestration