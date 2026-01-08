# 📄 FileForge - Enterprise File Processing Platform

A production-ready, scalable file processing platform similar to iLovePDF/SmallPDF. Built with Next.js, FastAPI, and modern cloud infrastructure.

## ✨ Features

- **PDF Tools**: Merge, split, compress, convert PDFs
- **Document Conversion**: PDF ↔ Word, Excel, Images
- **Image Processing**: Format conversion, compression, optimization
- **Batch Processing**: Handle multiple files simultaneously
- **User Management**: Guest and registered users with full authentication
- **Real-time Progress**: WebSocket-based job tracking
- **Cloud Storage**: S3-compatible storage with CDN support
- **Enterprise Security**: Rate limiting, file validation, CSRF protection

## 🚀 Tech Stack

### Frontend
- Next.js 14+ (App Router)
- TypeScript (Strict Mode)
- Tailwind CSS + ShadCN UI
- Framer Motion
- TanStack Query
- React Hook Form + Zod
- NextAuth.js

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL + SQLAlchemy (Async)
- Redis (Caching + Queue)
- Celery (Background Jobs)
- JWT Authentication
- S3-compatible Storage

### DevOps
- Docker + Docker Compose
- Nginx Reverse Proxy
- Multi-stage Builds
- CI/CD Ready

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## 🔧 Quick Start

### 1. Clone & Configure

```bash
git clone <repository>
cd pdf-combiner

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit .env files with your configuration
```

### 2. Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access the Platform

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

## 🛠️ Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
npm start
```

## 📁 Project Structure

```
pdf-combiner/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access
│   │   ├── workers/        # Background tasks
│   │   └── utils/          # Utilities
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── hooks/            # Custom hooks
│   ├── lib/              # Utilities
│   └── public/           # Static assets
├── nginx/                # Nginx configuration
└── docker-compose.yml    # Orchestration
```

## 🔒 Security Features

- JWT-based authentication with refresh tokens
- Rate limiting per IP and user
- File type validation (MIME + extension)
- Virus scanning integration ready
- CORS protection
- CSRF tokens
- Secure file upload/download with signed URLs
- Auto file cleanup (TTL-based)
- SQL injection prevention
- XSS protection

## 🎯 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### File Operations
- `POST /api/v1/tools/pdf/merge` - Merge PDFs
- `POST /api/v1/tools/pdf/split` - Split PDF
- `POST /api/v1/tools/pdf/compress` - Compress PDF
- `POST /api/v1/tools/convert/pdf-to-word` - PDF to Word
- `POST /api/v1/tools/convert/word-to-pdf` - Word to PDF
- `POST /api/v1/tools/convert/image-to-pdf` - Image to PDF
- `POST /api/v1/tools/convert/pdf-to-image` - PDF to Image
- `POST /api/v1/tools/image/convert` - Image format conversion

### Jobs & Status
- `GET /api/v1/jobs/{job_id}` - Get job status
- `GET /api/v1/jobs/{job_id}/download` - Download result
- `GET /api/v1/jobs/history` - User job history

## 🎨 Design System

The platform uses a modern, minimalist design with:
- Soft shadows and glassmorphism effects
- Smooth micro-interactions
- Comprehensive animation system
- Dark mode support
- Fully accessible (WCAG 2.1 AA)
- Mobile-first responsive design

## 📊 Performance

- Async I/O throughout
- Redis caching layer
- Connection pooling
- Lazy loading & code splitting
- Image optimization
- CDN-ready static assets
- Database query optimization
- Horizontal scaling ready

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 📈 Monitoring & Logging

- Structured JSON logging
- Health check endpoints
- Prometheus metrics ready
- Error tracking (Sentry integration ready)
- Performance monitoring

## 🚢 Production Deployment

### Environment Variables

See `.env.example` files for all required variables.

### Docker Production Build

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment

Platform is ready for:
- AWS (ECS, EKS, Lambda)
- GCP (Cloud Run, GKE)
- Azure (Container Instances, AKS)
- Vercel (Frontend)
- Railway, Render, Fly.io

## 🔄 Scaling Considerations

- Stateless architecture (horizontal scaling)
- Database read replicas
- Redis cluster for high availability
- CDN for static assets
- Load balancer ready
- Queue-based job processing
- Microservices architecture ready

## 📝 License

MIT License - feel free to use for commercial projects

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md

## 📞 Support

- Documentation: `/docs`
- API Reference: `http://localhost:8000/docs`
- Issues: GitHub Issues

---

Built with ❤️ for enterprise-grade file processing
