# Contributing to FileForge

Thank you for your interest in contributing to FileForge! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/pdf-combiner.git
   cd pdf-combiner
   ```

3. Copy environment files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```

4. Start development environment:
   ```bash
   docker-compose up -d
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development Workflow

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload

# Run tests
pytest

# Code formatting
black app/
isort app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Run type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, descriptive commit messages
   - Follow coding standards
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend && pytest

   # Frontend tests
   cd frontend && npm test

   # E2E tests
   npm run test:e2e
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Test additions/changes
   - `chore:` Build process or auxiliary tool changes

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Provide clear description of changes
   - Link related issues
   - Add screenshots for UI changes
   - Ensure CI passes

## Coding Standards

### Python (Backend)

- Follow PEP 8
- Use type hints
- Write docstrings for functions and classes
- Maximum line length: 100 characters
- Use Black for formatting
- Use isort for import sorting

Example:
```python
async def process_file(
    file_id: str,
    options: Dict[str, Any]
) -> ProcessedFile:
    """
    Process a file with given options.
    
    Args:
        file_id: Unique identifier for the file
        options: Processing options
        
    Returns:
        ProcessedFile instance
        
    Raises:
        ValueError: If file_id is invalid
    """
    pass
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow Airbnb style guide
- Use functional components with hooks
- Prefer const over let
- Use meaningful variable names
- Maximum line length: 100 characters

Example:
```typescript
interface ProcessFileOptions {
  compressionLevel: 'low' | 'medium' | 'high'
  quality?: number
}

export async function processFile(
  fileId: string,
  options: ProcessFileOptions
): Promise<ProcessedFile> {
  // Implementation
}
```

### CSS/Styling

- Use Tailwind CSS utility classes
- Follow mobile-first approach
- Use semantic class names for custom CSS
- Avoid inline styles

## Testing

### Backend Testing

```python
# test_service.py
import pytest
from app.services.file_service import FileService

@pytest.mark.asyncio
async def test_upload_file(db_session):
    service = FileService(db_session)
    result = await service.upload_file(mock_file)
    assert result.status == "success"
```

### Frontend Testing

```typescript
// component.test.tsx
import { render, screen } from '@testing-library/react'
import { FileUploader } from './file-uploader'

describe('FileUploader', () => {
  it('renders upload button', () => {
    render(<FileUploader />)
    expect(screen.getByText('Upload Files')).toBeInTheDocument()
  })
})
```

## Documentation

- Update README.md for significant changes
- Add JSDoc/docstrings for new functions
- Update API documentation
- Add comments for complex logic

## Questions?

- Open an issue for bugs
- Start a discussion for feature requests
- Join our Discord for questions

Thank you for contributing to FileForge! 🚀
