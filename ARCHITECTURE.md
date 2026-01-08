# Architecture Overview

This document provides a comprehensive overview of the FileForge platform architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx Reverse Proxy                  │
│                    (Load Balancing, SSL, Rate Limiting)      │
└─────────────────────┬───────────────────────┬───────────────┘
                      │                       │
              ┌───────▼───────┐       ┌──────▼──────┐
              │   Frontend    │       │   Backend   │
              │   (Next.js)   │       │  (FastAPI)  │
              └───────┬───────┘       └──────┬──────┘
                      │                       │
                      │                   ┌───▼────┐
                      │                   │ Redis  │
                      │                   │ Cache  │
                      │                   └───┬────┘
                      │                       │
                      │                   ┌───▼────────┐
                      │                   │ PostgreSQL │
                      │                   │  Database  │
                      │                   └───┬────────┘
                      │                       │
                      │                   ┌───▼────────┐
                      │                   │  Celery    │
                      │                   │  Workers   │
                      │                   └────────────┘
                      │
              ┌───────▼──────────────────┐
              │   S3-Compatible Storage  │
              │    (File Storage)        │
              └──────────────────────────┘
```

## Frontend Architecture (Next.js)

### Directory Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── tools/             # Tool pages
│   ├── dashboard/         # User dashboard
│   └── auth/              # Authentication pages
├── components/
│   ├── ui/                # Reusable UI components
│   ├── layout/            # Layout components
│   ├── home/              # Home page sections
│   └── tools/             # Tool-specific components
├── lib/
│   ├── api-client.ts      # API client
│   └── utils.ts           # Utility functions
├── hooks/                 # Custom React hooks
└── styles/                # Global styles
```

### Key Technologies

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **ShadCN UI**: Accessible component library
- **Framer Motion**: Animation library
- **TanStack Query**: Data fetching and caching
- **NextAuth.js**: Authentication
- **Zod**: Schema validation
- **React Hook Form**: Form management

### State Management

- **TanStack Query**: Server state
- **Zustand**: Client state (optional)
- **React Context**: Theme, auth

### Data Flow

1. User interacts with UI component
2. Component calls API client function
3. TanStack Query handles request, caching, and state
4. UI updates based on query state (loading, success, error)

## Backend Architecture (FastAPI)

### Directory Structure

```
backend/
├── app/
│   ├── main.py                 # Application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── router.py       # Main API router
│   │       └── routes/         # Route modules
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── security.py        # Auth utilities
│   │   └── logging.py         # Logging setup
│   ├── models/
│   │   └── models.py          # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/              # Business logic
│   ├── repositories/          # Data access layer
│   ├── workers/               # Celery tasks
│   ├── utils/                 # Utilities
│   └── db/
│       ├── base.py            # Database base
│       └── session.py         # Session management
└── tests/                     # Test suite
```

### Layered Architecture

```
┌─────────────────────────────────────┐
│          API Routes Layer           │
│    (Request/Response handling)      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Service Layer                │
│      (Business Logic)               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Repository Layer               │
│      (Data Access)                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Database Layer              │
│    (SQLAlchemy Models)              │
└─────────────────────────────────────┘
```

### Key Technologies

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM with async support
- **Alembic**: Database migrations
- **Pydantic V2**: Data validation
- **Celery**: Background task processing
- **Redis**: Caching and message broker
- **PostgreSQL**: Primary database
- **PyPDF2**: PDF processing
- **Pillow**: Image processing
- **Boto3**: S3 integration

### Request Flow

1. Client sends HTTP request to API endpoint
2. Middleware processes request (CORS, auth, rate limiting)
3. Router routes to appropriate handler
4. Handler validates request with Pydantic schema
5. Service layer executes business logic
6. Repository layer interacts with database
7. Response is serialized and returned

### Background Processing

```
┌──────────────┐
│  API Request │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Create Job   │
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌─────────────┐
│ Queue Task   ├─────►│    Redis    │
└──────────────┘      │   Broker    │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │   Celery    │
                      │   Worker    │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │  Process    │
                      │    File     │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │  Update Job │
                      │   Status    │
                      └─────────────┘
```

## Database Schema

### Users Table
- id (PK)
- email (unique, indexed)
- hashed_password
- role (guest, user, premium, admin)
- created_at, updated_at

### Jobs Table
- id (PK)
- job_id (unique, indexed)
- user_id (FK, nullable for guests)
- guest_token (indexed)
- tool_name
- status (pending, processing, completed, failed)
- progress (0-100)
- created_at, expires_at

### Files Table
- id (PK)
- file_id (unique, indexed)
- user_id (FK, nullable)
- guest_token (indexed)
- original_filename
- stored_filename
- file_size
- mime_type
- created_at, expires_at

## Security

### Authentication
- JWT-based authentication
- Access tokens (short-lived)
- Refresh tokens (long-lived)
- Guest tokens for anonymous users

### Authorization
- Role-based access control (RBAC)
- User roles: guest, user, premium, admin

### File Security
- MIME type validation
- File size limits
- Virus scanning (integration ready)
- Automatic file deletion (24-hour TTL)
- Signed URLs for downloads

### Network Security
- HTTPS/TLS encryption
- CORS configuration
- Rate limiting
- CSRF protection
- Security headers (HSTS, CSP, etc.)

## Scalability

### Horizontal Scaling

1. **Frontend**: Stateless Next.js instances
2. **Backend**: Multiple FastAPI workers
3. **Celery**: Multiple worker instances
4. **Database**: Read replicas, connection pooling
5. **Redis**: Redis Cluster for high availability

### Caching Strategy

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│  Check Redis │
│    Cache     │
└──────┬───────┘
       │
   ┌───▼────┐
   │ Hit?   │
   └───┬────┘
       │
  ┌────┴────┐
  │         │
Yes│        │No
  │         │
  ▼         ▼
Return  Query DB
Cache   & Cache
```

### Load Balancing

Nginx distributes traffic across multiple instances:
- Round-robin for API requests
- Sticky sessions for WebSocket connections
- Health checks for automatic failover

## Monitoring & Logging

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation (ELK stack ready)

### Metrics
- Prometheus metrics export
- Application metrics (request rate, latency)
- System metrics (CPU, memory, disk)
- Business metrics (files processed, users)

### Error Tracking
- Sentry integration ready
- Error alerting
- Performance monitoring

### Health Checks
- `/health` endpoint for basic health
- Database connectivity check
- Redis connectivity check
- Disk space check

## Deployment

### Container Orchestration
- Docker Compose (development)
- Kubernetes (production, optional)
- Docker Swarm (production, alternative)

### CI/CD Pipeline
```
┌──────────────┐
│  Git Push    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Run Tests  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Build Images│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Push Registry│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Deploy    │
└──────────────┘
```

### Cloud Deployment Options

1. **AWS**
   - ECS/EKS for containers
   - RDS for PostgreSQL
   - ElastiCache for Redis
   - S3 for file storage
   - CloudFront CDN

2. **GCP**
   - Cloud Run/GKE
   - Cloud SQL
   - Memorystore
   - Cloud Storage
   - Cloud CDN

3. **Azure**
   - Container Instances/AKS
   - Azure Database
   - Azure Cache
   - Blob Storage
   - Azure CDN

## Performance Optimizations

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Static generation where possible
- CDN for static assets

### Backend
- Database connection pooling
- Query optimization with indexes
- Async I/O throughout
- Redis caching
- Response compression

### File Processing
- Streaming for large files
- Chunked uploads
- Background processing with Celery
- Resource limits per task

## Disaster Recovery

### Backup Strategy
- Database: Daily automated backups
- Files: Replicated to backup storage
- Configuration: Version controlled

### Recovery Plan
1. Database restoration from backup
2. File storage restoration
3. Application redeployment
4. DNS failover to backup region

## Future Enhancements

- WebSocket support for real-time updates
- GraphQL API option
- Microservices architecture
- Multi-region deployment
- ML-powered file optimization
- Mobile apps (React Native)
- Desktop apps (Electron)

---

This architecture supports millions of users while maintaining high availability, security, and performance.
