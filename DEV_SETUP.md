# Development Setup Guide

Quick start guide for local development.

## Prerequisites

- Docker Desktop or Docker + Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)
- Git

## Quick Start (Docker)

```bash
# Clone repository
git clone <repository-url>
cd pdf-combiner

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (optional)

## Local Development (without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database (ensure PostgreSQL is running)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Database Setup

### Using Docker Compose

Database is automatically created when you run `docker-compose up`.

### Manual PostgreSQL Setup

```bash
# Create database
createdb fileforge

# Create user
psql -c "CREATE USER fileforge WITH PASSWORD 'fileforge_dev_pass';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE fileforge TO fileforge;"

# Run migrations
cd backend
alembic upgrade head
```

## Testing

### Backend Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_auth.py
```

### Frontend Tests

```bash
cd frontend
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

## Code Quality

### Backend

```bash
cd backend

# Formatting
black app/

# Import sorting
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

### Frontend

```bash
cd frontend

# Linting
npm run lint

# Type checking
npm run type-check

# Formatting (if configured)
npm run format
```

## Common Tasks

### Create Database Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

### Add New Tool

1. Create service method in `backend/app/services/tool_service.py`
2. Create Celery task in `backend/app/workers/tasks.py`
3. Add route in `backend/app/api/v1/routes/tools.py`
4. Create frontend component in `frontend/components/tools/`
5. Add route in `frontend/app/tools/`

### Environment Variables

See `.env.example` files for all available options.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Error

1. Ensure PostgreSQL is running
2. Check DATABASE_URL in `.env`
3. Verify credentials

### Module Not Found

```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### Docker Issues

```bash
# Remove all containers and rebuild
docker-compose down -v
docker-compose up --build

# Clean Docker system
docker system prune -a
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Docker

Settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. Open backend folder as project
2. Configure Python interpreter (virtual environment)
3. Enable Django support (for better FastAPI support)
4. Configure code style to use Black

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)

## Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [API.md](API.md) for API reference
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Open an issue on GitHub
