# Task Management API v2.0

A production-ready FastAPI application built with Domain-Driven Design (DDD) architecture, featuring user authentication, PostgreSQL persistence, comprehensive task management capabilities, and **97% test coverage**.

## ✨ Features

- 🔐 **User Authentication**: JWT-based authentication with secure password hashing
- 👤 **User Management**: Sign up, login, logout, and profile management
- 📋 **Task Management**: Create, read, update, and delete user-specific tasks
- 🏗️ **DDD Architecture**: Clean separation of domain, application, infrastructure, and presentation layers
- 🐘 **PostgreSQL Database**: Persistent storage with migrations using Alembic
- 🐳 **Docker Support**: Containerized database for local development
- 📖 **API Documentation**: Automatic OpenAPI/Swagger documentation
- 🔒 **Security**: Password validation, JWT tokens, CORS configuration
- 📄 **Pagination**: Efficient task listing with pagination support
- 🎯 **Type Safety**: Full type hints throughout the codebase
- ✅ **Comprehensive Testing**: 97% test coverage with unit and integration tests
- 🛠️ **Development Tools**: Makefile automation, tox environments, pre-commit hooks
- 📊 **Code Quality**: Automated linting, formatting, type checking, and security scanning

## 🚀 Quick Start

### Prerequisites
- Python 3.8.1+ (supports 3.8.1-3.13.1)
- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone and setup the project**:
```bash
git clone <your-repo-url>
cd talk-repo
make install    # or: uv sync --dev
```

3. **Start the PostgreSQL database and run migrations**:
```bash
make docker-up  # or: docker-compose -f docker-compose.test.yml up -d && uv run alembic upgrade head
```

4. **Start the application**:
```bash
make serve      # or: uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 🏥 Health Check
Visit `http://localhost:8000/health` to verify the application is running.

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## 🔗 API Endpoints

### 🔐 Authentication Endpoints

#### Sign Up
- **POST** `/api/v1/auth/signup`
- **Body**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123"
}
```
- **Response**: `201 Created` - User created with access tokens

#### Login
- **POST** `/api/v1/auth/login`
- **Body**:
```json
{
  "email": "user@example.com", 
  "password": "SecurePassword123"
}
```
- **Response**: `200 OK` - User authenticated with access tokens

#### Get Current User
- **GET** `/api/v1/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK` - Current user information

#### Logout
- **POST** `/api/v1/auth/logout`
- **Response**: `200 OK` - Logout successful (client should discard tokens)

### 📋 Task Endpoints (Authentication Required)

#### Get User's Tasks
- **GET** `/api/v1/tasks/?page=1&page_size=20&completed=false`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK` - Paginated list of user's tasks

#### Get Single Task
- **GET** `/api/v1/tasks/{task_id}`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK` - Task details (only if user owns the task)

#### Create Task
- **POST** `/api/v1/tasks/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**:
```json
{
  "title": "Learn DDD Architecture",
  "description": "Study Domain-Driven Design patterns"
}
```
- **Response**: `201 Created` - Created task

#### Update Task
- **PUT** `/api/v1/tasks/{task_id}`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description", 
  "completed": true
}
```
- **Response**: `200 OK` - Updated task

#### Delete Task
- **DELETE** `/api/v1/tasks/{task_id}`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `204 No Content` - Task deleted successfully

## 💡 Example Usage

### 1. Sign up a new user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johnsmith", 
    "password": "SecurePassword123"
  }'
```

### 2. Login and get access token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123" 
  }'
```

### 3. Create a task (use the access_token from step 2)
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Learn Domain-Driven Design",
    "description": "Study DDD patterns and architecture"
  }'
```

### 4. Get your tasks
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/v1/tasks/?page=1&page_size=10"
```

### 5. Update a task
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/TASK_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"completed": true}'
```

## 🏗️ Project Architecture (DDD)

```
task-management-api/
├── domain/                    # 🎯 Domain Layer
│   ├── entities/             # Domain entities (User, Task)
│   ├── value_objects/        # Value objects (UserId, Email, Password)
│   ├── repositories/         # Repository interfaces
│   └── services/             # Domain services
├── application/              # 📋 Application Layer  
│   ├── use_cases/           # Business use cases
│   ├── dto/                 # Data transfer objects
│   └── services/            # Application services
├── infrastructure/          # 🔧 Infrastructure Layer
│   ├── database/           # Database models and connections
│   ├── repositories/       # Repository implementations
│   ├── auth/              # Authentication services
│   └── config/            # Configuration settings
├── presentation/           # 🌐 Presentation Layer
│   ├── api/               # API endpoints and routers
│   ├── middleware/        # Authentication middleware
│   └── schemas/           # Request/response schemas
├── alembic/               # Database migrations
├── docker-compose.test.yml # PostgreSQL container
├── main.py               # FastAPI application entry point
└── pyproject.toml        # Project dependencies
```

## 🔒 Security Features

- **Password Hashing**: Secure bcrypt hashing
- **JWT Tokens**: Access and refresh token system
- **Input Validation**: Pydantic models with validation rules
- **CORS Configuration**: Configurable cross-origin resource sharing
- **User Authorization**: Users can only access their own data

## 🗄️ Database

The application uses PostgreSQL with the following key features:
- **Migrations**: Alembic for database schema versioning
- **Async Operations**: AsyncPG driver for high performance
- **Connection Pooling**: SQLAlchemy async engine
- **Indexed Queries**: Optimized database indexes

## 🧪 Environment Configuration

Create a `.env` file for custom configuration:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/db
JWT_SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🛠️ Development

### Database Operations
```bash
# Create new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## 🧪 Testing & Development

### Quick Testing Commands
```bash
# Run unit tests (fast)
make test-unit

# Run full test suite with database
make test

# Generate coverage report (opens in browser)
make coverage

# Run code quality checks
make lint           # Linting
make format         # Auto-format code
make type-check     # Type checking
make security       # Security scan

# Full CI pipeline (all checks + tests)
make ci
```

### Advanced Testing
```bash
# Run specific test environments
uv run tox -e py313     # Test on Python 3.13
uv run tox -e lint      # Run linting only
uv run tox -e type      # Run type checking only
uv run tox -e security  # Run security scan only

# Run integration tests only
make test-integration
```

### Test Coverage
- **Current Coverage**: 97.16%
- **Unit Tests**: 68 tests covering domain, application, and infrastructure layers
- **Integration Tests**: API endpoint tests with database
- **Coverage Reports**: Available in `htmlcov/` directory

### Docker Management
```bash
# Start test database
make docker-up

# Stop test database
make docker-down

# Clean database volumes (deletes all data!)
make docker-clean

# Check project status
make status
```

## 🛠️ Available Make Commands

Run `make help` to see all available commands:

```bash
Development Setup:
  make install         # Install all dependencies
  make dev             # Setup development environment

Testing:
  make test            # Run full test suite with Docker database
  make test-unit       # Run unit tests only (fast)
  make test-integration # Run integration tests with database
  make coverage        # Generate HTML coverage reports

Code Quality:
  make lint            # Run linting checks
  make format          # Auto-format code (black + isort)
  make format-check    # Check formatting without changes
  make type-check      # Run mypy type checking
  make security        # Run bandit security scan

Docker Management:
  make docker-up       # Start test database
  make docker-down     # Stop test database  
  make docker-clean    # Stop and remove database volumes

Workflows:
  make ci              # Full CI pipeline (format-check + lint + type + security + test)
  make clean           # Clean up generated files
```

## 🚀 Production Deployment

For production deployment, consider:
- Set strong JWT secret keys
- Configure proper CORS origins
- Use environment-specific database URLs
- Enable HTTPS
- Add rate limiting
- Implement proper logging
- Add health checks and monitoring

## 📈 Performance Features

- **Async/Await**: Non-blocking database operations
- **Connection Pooling**: Efficient database connections  
- **Pagination**: Memory-efficient data loading
- **Database Indexes**: Optimized query performance
- **JWT Stateless Auth**: No server-side session storage

## 📊 Code Quality & Testing

This project maintains high code quality standards:

- **97.16% Test Coverage**: Comprehensive unit and integration tests
- **Automated Testing**: Tox environments for Python 3.8.1-3.13.1
- **Code Formatting**: Black and isort for consistent styling
- **Linting**: Flake8 for code quality checks
- **Type Checking**: MyPy for static type analysis
- **Security Scanning**: Bandit for security vulnerability detection
- **Pre-commit Hooks**: Automated code quality checks on commit

---

**Built with ❤️ using FastAPI, PostgreSQL, and Domain-Driven Design principles.**