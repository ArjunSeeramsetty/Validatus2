# Validatus2 - Complete Deployment Guide

**Last Updated**: October 16, 2025  
**Platform**: Google Cloud Platform (Cloud Run)  
**Current Version**: Backend 00182-4gm | Frontend Latest  

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [GCP Deployment](#gcp-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Security & Authentication](#security--authentication)
8. [Monitoring & Logging](#monitoring--logging)
9. [Troubleshooting](#troubleshooting)
10. [Windows-Specific Guide](#windows-specific-guide)

---

## Quick Start

### Deploy to GCP (Fastest)

```bash
# 1. Clone repository
git clone https://github.com/ArjunSeeramsetty/Validatus2.git
cd Validatus2

# 2. Configure GCP
gcloud config set project validatus-platform
gcloud auth login

# 3. Deploy backend
cd backend
gcloud builds submit --config=cloudbuild.yaml

# 4. Deploy frontend (optional)
cd ../frontend
npm install
npm run build
# Deploy dist/ to your hosting service
```

### Run Locally (Development)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## Prerequisites

### Required Tools

- **Python**: 3.11+
- **Node.js**: 18+
- **Git**: Latest
- **Google Cloud SDK**: Latest
- **PostgreSQL**: 14+ (for local development)

### GCP Services Required

- **Cloud Run**: For backend API
- **Cloud SQL**: PostgreSQL database
- **Cloud Build**: CI/CD
- **Secret Manager**: For sensitive configs
- **Cloud Storage**: File storage (optional)

### API Keys Required

- **Google Gemini API**: For LLM analysis
- **Google Custom Search API**: For web search
- **Google Cloud credentials**: For GCP services

---

## Local Development Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your backend URL

# Start development server
npm run dev
```

### 3. Database Setup (Local PostgreSQL)

```bash
# Create database
createdb validatus_dev

# Run migrations
cd backend
alembic upgrade head

# Verify schema
psql validatus_dev -c "\dt"
```

---

## GCP Deployment

### Backend Deployment

#### Option 1: Automated (Cloud Build)

```bash
cd backend

# Deploy using Cloud Build
gcloud builds submit --config=cloudbuild.yaml --project=validatus-platform

# Traffic will automatically route to new revision
```

#### Option 2: Manual (gcloud CLI)

```bash
cd backend

# Build container
gcloud builds submit --tag gcr.io/validatus-platform/validatus-backend

# Deploy to Cloud Run
gcloud run deploy validatus-backend \
  --image gcr.io/validatus-platform/validatus-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://...,GEMINI_API_KEY=..." \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10
```

### Frontend Deployment

#### Option 1: Cloud Run (Static Hosting)

```bash
cd frontend

# Build production bundle
npm run build

# Deploy to Cloud Run
gcloud run deploy validatus-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Option 2: Firebase Hosting

```bash
cd frontend

# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Build and deploy
npm run build
firebase deploy --only hosting
```

---

## Environment Configuration

### Backend Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/validatus
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Google APIs
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CUSTOM_SEARCH_API_KEY=your_search_api_key
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id

# Google Cloud
GOOGLE_CLOUD_PROJECT=validatus-platform
GCS_BUCKET_NAME=validatus-storage

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend-domain.com

# Optional: Monitoring
ENABLE_MONITORING=true
MONITORING_PROJECT_ID=validatus-platform
```

### Frontend Environment Variables

```bash
# API Configuration
VITE_API_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app
VITE_API_TIMEOUT=30000

# Feature Flags
VITE_ENABLE_ENHANCED_ANALYSIS=true
VITE_ENABLE_PATTERN_LIBRARY=true

# Analytics (optional)
VITE_GA_TRACKING_ID=your_ga_id
```

---

## Database Setup

### Cloud SQL Setup

```bash
# 1. Create Cloud SQL instance
gcloud sql instances create validatus-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-2-8192 \
  --region=us-central1 \
  --backup \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=3

# 2. Create database
gcloud sql databases create validatus --instance=validatus-db

# 3. Create user
gcloud sql users create validatus-user \
  --instance=validatus-db \
  --password=STRONG_PASSWORD_HERE

# 4. Get connection name
gcloud sql instances describe validatus-db --format="value(connectionName)"

# 5. Connect from Cloud Run
# Use Unix socket: /cloudsql/PROJECT:REGION:INSTANCE
```

### Database Schema

Schema is automatically created via Alembic migrations:

```bash
# Run migrations
alembic upgrade head

# Check current version
alembic current

# View migration history
alembic history
```

**Key Tables**:
- `topics` - Topic configurations
- `topic_urls` - Collected URLs
- `scraped_content` - Scraped content
- `v2_analysis_results` - Scoring results
- `v2_expert_persona_scorer` - Expert scores

---

## Security & Authentication

### API Authentication

Currently using **public endpoints** for development. For production:

```python
# Add authentication middleware
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/protected")
async def protected_route(token: str = Security(security)):
    # Verify token
    if not verify_token(token):
        raise HTTPException(status_code=401)
    return {"message": "Authorized"}
```

### Secret Management

Store sensitive data in GCP Secret Manager:

```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:PROJECT-NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Use in Cloud Run
gcloud run services update validatus-backend \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest
```

### CORS Configuration

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "http://localhost:3000"  # Development only
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Monitoring & Logging

### Cloud Logging

View logs:
```bash
# Backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend" --limit 50

# Filter by severity
gcloud logging read "severity>=ERROR" --limit 20
```

### Cloud Monitoring

**Metrics to Monitor**:
- Request latency (p50, p95, p99)
- Error rate
- Memory usage
- CPU utilization
- Database connection pool

**Set up alerts**:
```bash
# High error rate alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

### Application Performance Monitoring

The application includes optional `performance_monitor` decorators:

```python
from app.middleware.monitoring import performance_monitor

@performance_monitor("operation_name")
async def my_function():
    # Function code
    pass
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```
Error: could not connect to server
```

**Solution**:
- Check Cloud SQL proxy configuration
- Verify DATABASE_URL format
- Ensure Cloud SQL instance is running
- Check IAM permissions

#### 2. CORS Errors in Frontend

```
Access to fetch has been blocked by CORS policy
```

**Solution**:
- Update `allow_origins` in backend
- Verify frontend URL matches CORS config
- Check for trailing slashes in URLs

#### 3. Memory Issues (Cloud Run)

```
Container terminated: Out of memory
```

**Solution**:
```bash
# Increase memory limit
gcloud run services update validatus-backend --memory 4Gi
```

#### 4. Cold Start Latency

```
Request timeout after 900 seconds
```

**Solution**:
```bash
# Enable minimum instances
gcloud run services update validatus-backend --min-instances 1

# Or increase CPU allocation
gcloud run services update validatus-backend --cpu 4
```

#### 5. Import Errors (Sophisticated Engines)

```
cannot import name 'monitoring_v3' from 'google.cloud'
```

**Solution**: Already fixed - monitoring imports are now optional with graceful degradation.

### Health Check Endpoints

```bash
# Backend health
curl https://validatus-backend-ssivkqhvhq-uc.a.run.app/health

# System status
curl https://validatus-backend-ssivkqhvhq-uc.a.run.app/api/v3/system/status

# Engine status
curl https://validatus-backend-ssivkqhvhq-uc.a.run.app/api/v3/enhanced-analysis/formula-status
```

---

## Windows-Specific Guide

### PowerShell Scripts

Located in `scripts/windows/`:

```powershell
# Setup environment
.\scripts\windows\setup-environment.ps1

# Deploy backend
.\scripts\windows\deploy-backend.ps1

# Run tests
.\scripts\windows\run-tests.ps1
```

### Virtual Environment (Windows)

```powershell
# Create venv
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### Common Windows Issues

#### 1. Long Path Names

```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solution**:
```powershell
# Enable long paths
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

#### 2. PostgreSQL Service

```powershell
# Start PostgreSQL service
Start-Service postgresql-x64-14

# Check status
Get-Service postgresql-x64-14
```

---

## Production Checklist

### Before Deployment

- [ ] Update environment variables
- [ ] Run all tests (`pytest`)
- [ ] Check linter errors (`flake8`, `eslint`)
- [ ] Review CORS configuration
- [ ] Update SECRET_KEY
- [ ] Configure database backups
- [ ] Set up monitoring alerts
- [ ] Test health endpoints
- [ ] Review resource limits (memory, CPU)
- [ ] Enable HTTPS
- [ ] Configure custom domain
- [ ] Set up CDN (optional)

### After Deployment

- [ ] Verify health endpoint responds
- [ ] Test API endpoints
- [ ] Check frontend loads correctly
- [ ] Monitor logs for errors
- [ ] Test database connectivity
- [ ] Verify pattern matching works
- [ ] Check Monte Carlo simulations
- [ ] Test Results tab displays data
- [ ] Verify all 5 segment tabs work
- [ ] Monitor memory usage
- [ ] Check response times

---

## CI/CD Pipeline

### Automated Deployment

**Cloud Build Configuration** (`backend/cloudbuild.yaml`):

```yaml
steps:
  # Build container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/validatus-backend', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/validatus-backend']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'validatus-backend'
      - '--image=gcr.io/$PROJECT_ID/validatus-backend'
      - '--region=us-central1'
      - '--platform=managed'

timeout: '1200s'
```

### GitHub Actions (Optional)

```yaml
# .github/workflows/deploy.yml
name: Deploy to GCP

on:
  push:
    branches: [master]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: validatus-platform
      
      - name: Deploy Backend
        run: |
          cd backend
          gcloud builds submit --config=cloudbuild.yaml
```

---

## Backup & Recovery

### Database Backups

```bash
# Enable automatic backups
gcloud sql instances patch validatus-db \
  --backup-start-time=03:00

# Manual backup
gcloud sql backups create --instance=validatus-db

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=validatus-db \
  --backup-id=BACKUP_ID
```

### Export Data

```bash
# Export database
gcloud sql export sql validatus-db \
  gs://validatus-backups/backup-$(date +%Y%m%d).sql \
  --database=validatus

# Import database
gcloud sql import sql validatus-db \
  gs://validatus-backups/backup-20241016.sql \
  --database=validatus
```

---

## Performance Optimization

### Backend Optimization

```python
# Connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Caching
REDIS_URL=redis://cache-host:6379/0

# Request timeout
TIMEOUT=900  # 15 minutes
```

### Frontend Optimization

```javascript
// Code splitting
const Results = lazy(() => import('./pages/Results'));

// Caching
const cache = new Cache({
  maxAge: 300000,  // 5 minutes
  maxSize: 100
});
```

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_urls_topic_id ON topic_urls(topic_id);
CREATE INDEX idx_content_topic_id ON scraped_content(topic_id);
CREATE INDEX idx_results_session_id ON v2_analysis_results(session_id);
```

---

## Support & Resources

### Documentation
- **Main Guide**: VALIDATUS2_COMPLETE_IMPLEMENTATION_GUIDE.md
- **API Reference**: docs/API_DOCUMENTATION.md
- **User Guide**: USER_GUIDE.md
- **Development**: DEVELOPMENT_HISTORY.md

### Endpoints
- **Backend**: https://validatus-backend-ssivkqhvhq-uc.a.run.app
- **Health**: https://validatus-backend-ssivkqhvhq-uc.a.run.app/health
- **API Docs**: https://validatus-backend-ssivkqhvhq-uc.a.run.app/docs

### Repository
- **GitHub**: https://github.com/ArjunSeeramsetty/Validatus2
- **Issues**: https://github.com/ArjunSeeramsetty/Validatus2/issues

---

**Last Updated**: October 16, 2025  
**Maintained by**: Validatus Development Team  
**Version**: 3.1.0

