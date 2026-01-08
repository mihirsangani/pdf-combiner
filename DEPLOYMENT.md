# Deployment Guide

Complete guide for deploying FileForge to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [SSL/TLS Setup](#ssltls-setup)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)

## Prerequisites

### Server Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 50GB SSD storage
- Ubuntu 20.04 LTS or similar

**Recommended:**
- 4+ CPU cores
- 8GB+ RAM
- 100GB+ SSD storage
- Ubuntu 22.04 LTS

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/pdf-combiner.git
cd pdf-combiner
```

### 2. Configure Environment Variables

**Backend (.env):**
```bash
cd backend
cp .env.example .env
nano .env
```

Update critical values:
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-strong-32+-char-secret>
JWT_SECRET_KEY=<generate-strong-32+-char-secret>
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/fileforge
REDIS_URL=redis://:password@redis:6379/0
CORS_ORIGINS=https://yourdomain.com
```

Generate secrets:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Frontend (.env.production):**
```bash
cd frontend
cp .env.example .env.production
nano .env.production
```

Update:
```env
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=<generate-strong-secret>
```

### 3. Configure Nginx

Update domain in `nginx/conf.d/default.conf`:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

## Docker Deployment

### Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3 --scale celery-worker=4
```

### Database Migration

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Stop nginx
docker-compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update docker-compose.prod.yml to mount certificates
# Add to nginx service:
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro

# Start nginx
docker-compose start nginx

# Auto-renewal (add to crontab)
0 0 * * * certbot renew --quiet --post-hook "docker-compose restart nginx"
```

### Option 2: Custom Certificate

Place certificates in `./certs/`:
```
certs/
├── fullchain.pem
└── privkey.pem
```

Update nginx configuration to use mounted certificates.

## Cloud Deployment

### AWS EC2 Deployment

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04
   - Instance type: t3.medium or larger
   - Security group: Allow 80, 443, 22

2. **Connect and Setup:**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <your-repo>
cd pdf-combiner
# Configure .env files
docker-compose -f docker-compose.prod.yml up -d
```

3. **Setup RDS (Optional):**
   - Create PostgreSQL RDS instance
   - Update DATABASE_URL in .env
   - Ensure security group allows connections

4. **Setup ElastiCache (Optional):**
   - Create Redis cluster
   - Update REDIS_URL in .env

5. **Setup S3:**
   - Create S3 bucket
   - Create IAM user with S3 access
   - Update environment variables:
```env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

### Google Cloud Platform

1. **Create VM Instance:**
```bash
gcloud compute instances create fileforge-vm \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB
```

2. **Setup similar to AWS**

3. **Use Cloud SQL for PostgreSQL**

4. **Use Cloud Storage for files**

### Kubernetes (Advanced)

See `k8s/` directory for Kubernetes manifests (to be created if needed).

## Monitoring

### Health Checks

```bash
# Application health
curl https://yourdomain.com/health

# Backend health
curl https://yourdomain.com/api/v1/health
```

### Logs

```bash
# View all logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Export logs
docker-compose logs > app.log
```

### Metrics (Prometheus + Grafana)

Add to docker-compose:
```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Backup & Recovery

### Database Backup

**Automated Daily Backup:**
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
docker-compose exec -T postgres pg_dump -U fileforge fileforge > "$BACKUP_DIR/db_$DATE.sql"
# Compress
gzip "$BACKUP_DIR/db_$DATE.sql"
# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Add to crontab
0 2 * * * /path/to/backup.sh
```

**Manual Backup:**
```bash
docker-compose exec postgres pg_dump -U fileforge fileforge > backup.sql
```

**Restore:**
```bash
docker-compose exec -T postgres psql -U fileforge fileforge < backup.sql
```

### File Backup

If using local storage:
```bash
# Backup uploads
tar -czf uploads_backup.tar.gz backend/uploads/

# Restore
tar -xzf uploads_backup.tar.gz -C backend/
```

If using S3: Enable versioning and lifecycle policies.

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong secret keys
- [ ] Enable HTTPS with valid certificate
- [ ] Configure firewall (ufw/security groups)
- [ ] Set up automated backups
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Implement log rotation

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart service
docker-compose restart backend
```

### Database connection issues

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U fileforge -c "SELECT 1;"

# Check connection string in .env
# Verify DATABASE_URL format
```

### High memory usage

```bash
# Check resource usage
docker stats

# Limit resources in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

### Celery workers not processing

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Restart workers
docker-compose restart celery-worker

# Check worker logs
docker-compose logs celery-worker
```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_jobs_created ON jobs(created_at);
CREATE INDEX idx_files_expires ON files(expires_at);

-- Analyze tables
ANALYZE jobs;
ANALYZE files;
```

### Redis Configuration

Update redis.conf:
```
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Nginx Optimization

```nginx
worker_processes auto;
worker_connections 2048;
keepalive_timeout 30;

# Enable caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend
docker-compose up -d --scale backend=3

# Scale celery workers
docker-compose up -d --scale celery-worker=5

# Use load balancer (nginx upstream)
```

### Vertical Scaling

Upgrade server resources (CPU, RAM, storage).

## Support

For issues:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review logs
- Open GitHub issue
- Contact support

---

**Next Steps:**
- Set up monitoring
- Configure automated backups
- Enable SSL
- Test disaster recovery
- Review security settings
