# FastAPI Industry-Standard Template

A production-ready FastAPI AI API with PostgreSQL, MongoDB, JWT authentication, Docker support, and industry best practices. This template provides a solid foundation for building scalable RESTful APIs.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs with automatic OpenAPI documentation
- **PostgreSQL** - Primary SQL database with SQLAlchemy ORM and async support
- **MongoDB** - NoSQL database support with Motor async driver
- **JWT Authentication** - Secure token-based authentication with access/refresh tokens
- **Docker** - Complete containerization with Docker Compose for development and production
- **Repository Pattern** - Clean separation of data access logic with abstract base classes
- **Layered Architecture** - Well-structured codebase following industry best practices
- **API Versioning** - Versioned API endpoints (`/api/v1/`) for future compatibility
- **Error Handling** - Comprehensive error handling with global exception handlers
- **Health Checks** - Database and service health monitoring endpoints
- **Database Migrations** - Alembic integration for schema version control
- **Testing** - Comprehensive test suite with pytest and coverage
- **Logging** - Structured logging with request tracking and correlation IDs

## 📁 Project Structure

```
fastapi-template/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # Application entry point and FastAPI app creation
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   ├── deps.py               # API-specific dependencies (auth, db sessions)
│   │   └── v1/                   # API version 1
│   │       ├── __init__.py
│   │       ├── router.py         # Main v1 router aggregator
│   │       └── endpoints/         # Route handlers
│   │           ├── __init__.py
│   │           ├── auth.py       # Authentication endpoints
│   │           ├── users.py      # User CRUD endpoints
│   │           └── health.py     # Health check endpoints
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management (Pydantic Settings)
│   │   ├── security.py           # JWT, password hashing utilities
│   │   └── logging.py            # Logging configuration
│   │
│   ├── db/                       # Database layer
│   │   ├── __init__.py
│   │   ├── session.py           # SQLAlchemy session management
│   │   ├── base.py              # Base class for SQL models
│   │   ├── mongodb.py           # MongoDB connection management
│   │   └── init_db.py           # Database initialization
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # SQLAlchemy models
│   │   └── mongo/               # MongoDB documents/models
│   │       ├── __init__.py
│   │       └── document.py      # MongoDB document schemas
│   │
│   ├── schemas/                  # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user.py              # User schemas (create, update, response)
│   │   ├── token.py             # JWT token schemas
│   │   └── response.py          # Common response schemas
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py      # Business logic for users
│   │   └── auth_service.py      # Authentication business logic
│   │
│   ├── repositories/             # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py              # Base repository pattern
│   │   ├── user_repository.py   # User data access layer
│   │   └── mongo_repository.py   # MongoDB repository base
│   │
│   └── middleware/               # Custom middleware
│       ├── __init__.py
│       ├── error_handler.py     # Global exception handlers
│       └── logging.py           # Request/response logging
│
├── alembic/                     # Database migrations
│   ├── env.py                   # Alembic environment configuration
│   ├── script.py.mako          # Migration file template
│   └── versions/                # Migration files directory
│
├── scripts/                     # Utility scripts
│   ├── init_db.py              # Database initialization script
│   └── create_superuser.py     # Admin user creation script
│
├── docker/                      # Docker configuration
│   ├── Dockerfile              # Multi-stage Docker build
│   └── docker-compose.yml      # Docker Compose services
│
├── .env.sample                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Project metadata and tool configs
└── README.md                  # This file
```

## 🏗️ Architecture Overview

### Layered Architecture

- **API Layer** (`api/`): Route handlers and request/response handling
- **Service Layer** (`services/`): Business logic and orchestration
- **Repository Layer** (`repositories/`): Data access abstraction
- **Models/Schemas**: Clear separation between DB models and API schemas

### Key Design Patterns

- **Repository Pattern**: Abstract data access with concrete implementations
- **Dependency Injection**: FastAPI's built-in DI for clean architecture
- **Factory Pattern**: Service and repository instantiation
- **Strategy Pattern**: Multiple database support (SQL + NoSQL)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git
- PDM (optional but recommended for dependency management)

### Option 1: Docker (Recommended for Development)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd fastapi-template
   ```

2. **Set up environment variables**

   ```bash
   cp .env.sample .env
   # Edit .env with your configuration (optional for development)
   ```

3. **Start all services**

   ```bash
   cd docker
   docker-compose up -d
   ```

4. **Run database migrations**

   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Create a superuser (optional)**

   ```bash
   docker-compose exec app python scripts/create_superuser.py
   ```

6. **Access the application**
   - **API**: http://localhost:8000
   - **Interactive API docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/api/v1/health/health

### Option 2: Local Development

1. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   **Option A: Using PDM (Recommended)**

   ```bash
   # Install PDM if not already installed
   pip install pdm

   # Install dependencies using PDM
   pdm install

   # Export requirements for Docker/deployment
   pdm export -o requirements.txt --no-hashes
   pdm export -o requirements-dev.txt --dev --no-hashes
   ```

   **Option B: Using pip**

   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Set up databases**

   - Install and start PostgreSQL locally
   - Install and start MongoDB locally
   - Update `.env` with your database credentials

4. **Set up environment variables**

   ```bash
   cp .env.sample .env
   # Edit .env with your local database settings
   ```

5. **Run database migrations**

   ```bash
   alembic upgrade head
   ```

6. **Create a superuser (optional)**

   ```bash
   python scripts/create_superuser.py
   ```

7. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint                | Description           | Auth Required |
| ------ | ----------------------- | --------------------- | ------------- |
| POST   | `/api/v1/auth/login`    | User login            | No            |
| POST   | `/api/v1/auth/refresh`  | Refresh access token  | No            |
| GET    | `/api/v1/auth/me`       | Get current user info | Yes           |
| POST   | `/api/v1/auth/register` | User registration     | No            |

### User Management Endpoints

| Method | Endpoint                             | Description     | Auth Required | Role Required  |
| ------ | ------------------------------------ | --------------- | ------------- | -------------- |
| GET    | `/api/v1/users/`                     | List users      | Yes           | Superuser      |
| GET    | `/api/v1/users/{user_id}`            | Get user by ID  | Yes           | User/Superuser |
| PUT    | `/api/v1/users/{user_id}`            | Update user     | Yes           | User/Superuser |
| DELETE | `/api/v1/users/{user_id}`            | Delete user     | Yes           | Superuser      |
| PATCH  | `/api/v1/users/{user_id}/activate`   | Activate user   | Yes           | Superuser      |
| PATCH  | `/api/v1/users/{user_id}/deactivate` | Deactivate user | Yes           | Superuser      |

### Health Check Endpoints

| Method | Endpoint                | Description                | Auth Required |
| ------ | ----------------------- | -------------------------- | ------------- |
| GET    | `/api/v1/health/health` | Comprehensive health check | No            |
| GET    | `/api/v1/health/ping`   | Simple ping endpoint       | No            |

### Example API Usage

**Login:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Get current user:**

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## ⚙️ Configuration

The application uses environment variables for configuration. Copy `.env.sample` to `.env` and update the values:

```bash
# Application Settings
APP_NAME="FastAPI AI API"
DEBUG=false
ENVIRONMENT=production

# API Configuration
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# PostgreSQL Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=fastapi_db
POSTGRES_PORT=5432

# MongoDB Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fastapi_mongo

# Redis Cache
REDIS_URL=redis://localhost:6379

# CORS Settings
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Security
ALGORITHM=HS256
```

## 📦 Dependency Management with PDM

This project uses [PDM](https://pdm.fming.dev/) for modern Python dependency management. PDM provides faster dependency resolution and better lock file management compared to pip.

### PDM Commands

```bash
# Install PDM globally
pip install pdm

# Initialize PDM in the project (if not already done)
pdm init

# Install all dependencies (production + development)
pdm install

# Install only production dependencies
pdm install --prod

# Add a new dependency
pdm add fastapi
pdm add --dev pytest

# Add a dependency with specific version
pdm add "sqlalchemy>=2.0.0"

# Remove a dependency
pdm remove package-name

# Update dependencies
pdm update

# Update specific dependency
pdm update fastapi

# Show dependency tree
pdm list --tree

# Export requirements for deployment
pdm export -o requirements.txt --no-hashes
pdm export -o requirements-dev.txt --dev --no-hashes

# Show outdated packages
pdm outdated

# Sync virtual environment with lock file
pdm sync
```

### PDM Configuration

The project is configured with:

- **Python version**: >=3.11 (defined in `pyproject.toml`)
- **Dependencies**: Listed in `pyproject.toml` under `[project.dependencies]`
- **Dev dependencies**: Listed under `[project.optional-dependencies.dev]`
- **Lock file**: `pdm.lock` for reproducible builds

### Benefits of PDM

- **Faster resolution**: Uses `uv` backend for ultra-fast dependency resolution
- **Better lock files**: More reliable than pip's requirements.txt
- **PEP 621 compliant**: Uses standard `pyproject.toml` format
- **Virtual environment management**: Automatically manages venvs
- **Cross-platform**: Works consistently across different operating systems

## 🗄️ Database Management

### Migrations with Alembic

The project uses Alembic for database schema version control:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new field to users table"

# Apply migrations
alembic upgrade head

# Rollback to previous version
alembic downgrade -1

# Check current migration version
alembic current

# Show migration history
alembic history
```

### Database Initialization

```bash
# Initialize databases (PostgreSQL + MongoDB)
python scripts/init_db.py

# Create superuser account
python scripts/create_superuser.py
```

## 🧪 Testing

The project includes comprehensive testing setup with pytest:

```bash
# Run all tests with coverage (default configuration)
pdm run pytest

# Run with HTML coverage report
pdm run pytest --cov-report=html

# Run with XML coverage report (for CI/CD)
pdm run pytest --cov-report=xml

# Run with multiple coverage reports
pdm run pytest --cov-report=html --cov-report=xml --cov-report=term-missing

# Run specific test file
pdm run pytest tests/test_auth.py

# Run tests with verbose output
pdm run pytest -v

# Run tests in parallel (requires pytest-xdist)
pdm run pytest -n auto

# Run tests without coverage
pdm run pytest --no-cov

# Alternative: Run tests directly with pytest (if dependencies are installed)
pytest --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing
```

### Test Configuration

The project is configured with pytest and pytest-cov for comprehensive testing:

- **Coverage**: Automatically enabled with `--cov=app` in default configuration
- **Coverage Reports**: HTML, XML, and terminal output supported
- **Async Support**: pytest-asyncio configured for async test functions
- **Test Discovery**: Automatically finds test files matching `test_*.py` pattern
- **Coverage Exclusions**: Excludes test files, migrations, and alembic files

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py            # Authentication tests
├── test_users.py           # User management tests
├── test_health.py          # Health check tests
└── test_database.py        # Database tests
```

## 🐳 Docker Commands

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app bash

# Run migrations
docker-compose exec app alembic upgrade head

# Create superuser
docker-compose exec app python scripts/create_superuser.py

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Production

```bash
# Export requirements for Docker build (if using PDM)
pdm export -o requirements.txt --no-hashes
pdm export -o requirements-dev.txt --dev --no-hashes

# Build production image
docker build -f docker/Dockerfile -t fastapi-template:latest .

# Run production container
docker run -d -p 8000:8000 --env-file .env fastapi-template:latest
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schemas for request validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **Environment Variables**: Sensitive data stored in environment variables
- **Request Logging**: Comprehensive request/response logging
- **Error Handling**: Secure error responses without sensitive data exposure

## 📊 Monitoring & Logging

### Health Checks

- Database connectivity monitoring
- Service status reporting
- Response time tracking

### Logging

- Structured JSON logging
- Request correlation IDs
- Error tracking and reporting
- Performance metrics

## 🚀 Deployment

### Docker Deployment

1. Build production image
2. Configure environment variables
3. Run database migrations
4. Start container with proper networking

### Cloud Deployment

- **AWS**: ECS, Lambda, or EC2
- **Google Cloud**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **Heroku**: Container deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation for new features
- Use meaningful commit messages
- Keep pull requests focused and small

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code documentation
- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- SQLAlchemy team for the powerful ORM
- MongoDB team for the flexible NoSQL database
- All contributors and the open-source community

---

**Happy Coding! 🚀**

For more information, visit the [FastAPI documentation](https://fastapi.tiangolo.com/) or check out the interactive API documentation at `/docs` when running the application.
