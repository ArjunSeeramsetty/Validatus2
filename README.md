# 🏗️ Validatus - AI-Powered Strategic Analysis Platform

A cloud-native, AI-first architecture on Google Cloud Platform for comprehensive three-stage analytical workflows.

## 🎯 Overview

Validatus is an enterprise-grade platform that enables strategic analysis through three distinct stages:

1. **Knowledge Acquisition & Vector Store Creation** - Intelligent content collection and processing
2. **Strategic Analysis Execution** - AI-powered scoring and factor analysis  
3. **Results Dashboard & Visualization** - Interactive insights and reporting

## 🚀 Key Features

- **GCP-Native Architecture** - Built on Google Cloud Platform with enterprise scalability
- **AI-Powered Analysis** - Leverages Vertex AI and advanced ML models
- **Topic-Based Knowledge Management** - Organized vector stores for different analysis topics
- **Real-Time Processing** - Cloud Tasks and Pub/Sub for scalable job processing
- **Enterprise Security** - IAM, VPC, and comprehensive audit logging

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI with async/await support
- Google Cloud Platform services
- Vertex AI for embeddings and ML
- Cloud SQL (PostgreSQL) for structured data
- Firestore for document storage
- Cloud Storage for file management

**Infrastructure:**
- Terraform for Infrastructure as Code
- Cloud Run for containerized services
- Cloud Tasks for job queuing
- Pub/Sub for event-driven architecture

## 📋 Prerequisites

- Google Cloud Platform account with billing enabled
- Python 3.11+
- Docker (for containerization)
- Terraform (for infrastructure deployment)

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/validatus-platform.git
cd validatus-platform
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your GCP project details
```

### 3. Set Up GCP Infrastructure

```bash
cd infrastructure/terraform
terraform init
terraform plan -var="project_id=your-project-id"
terraform apply -var="project_id=your-project-id"
```

### 4. Deploy Backend Services

```bash
cd backend
pip install -r requirements-gcp.txt
python -m app.main
```

### 5. Run with Docker (Recommended)

```bash
# Build and run with GCP integration
docker build -f backend/Dockerfile.gcp -t validatus-backend .
docker run -p 8000:8000 --env-file .env validatus-backend
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

- `GCP_PROJECT_ID` - Your Google Cloud Project ID
- `CLOUD_SQL_INSTANCE` - Cloud SQL instance name
- `VERTEX_AI_LOCATION` - Vertex AI region
- `ALLOWED_ORIGINS` - CORS allowed origins

### GCP Services Required

The platform uses the following GCP services:
- Cloud Run (compute)
- Cloud SQL (database)
- Cloud Storage (file storage)
- Vertex AI (AI/ML)
- Cloud Tasks (job processing)
- Pub/Sub (messaging)
- Cloud Monitoring (observability)

## 📊 API Endpoints

### Topic Management

- `GET /api/v3/topics` - List all available topics
- `POST /api/v3/topics/create` - Create new topic vector store
- `POST /api/v3/topics/{topic}/collect-urls` - Collect URLs for topic
- `GET /api/v3/topics/{topic}/evidence/{layer}` - Retrieve evidence by layer

### Health & Monitoring

- `GET /health` - Health check endpoint

## 🧪 Testing

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## 📈 Monitoring

The platform includes comprehensive monitoring:

- **Cloud Monitoring** - Custom metrics and dashboards
- **Cloud Logging** - Centralized log aggregation
- **Error Reporting** - Automatic error tracking
- **Performance Monitoring** - Request tracing

## 🔒 Security

- **IAM Integration** - Role-based access control
- **VPC Security** - Network isolation
- **Secret Manager** - Secure credential storage
- **Audit Logging** - Complete audit trail

## 🚀 Deployment

### Development

```bash
# Local development with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# Deploy to Cloud Run
gcloud run deploy validatus-backend \
  --image gcr.io/your-project/validatus-backend:latest \
  --region us-central1 \
  --platform managed
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/)
- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder
- Review the architecture plan in `VALIDATUS_IMPLEMENTATION_PLAN.md`

---

**Built with ❤️ for enterprise-scale AI-powered strategic analysis**
