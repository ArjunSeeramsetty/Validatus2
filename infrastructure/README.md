# Validatus GCP Infrastructure

This directory contains the complete infrastructure setup for the Validatus platform on Google Cloud Platform.

## 🏗️ Architecture Overview

The Validatus platform uses the following GCP services:

- **Cloud SQL PostgreSQL**: Primary database for structured data
- **Cloud Storage**: Object storage for content, embeddings, and reports
- **Memorystore Redis**: Caching and session management
- **Cloud Spanner**: Analytics and cross-topic insights
- **Vertex AI**: Vector search and embeddings
- **Cloud Run**: Serverless application hosting
- **VPC Network**: Private networking with Cloud NAT

## 📁 Directory Structure

```
infrastructure/
├── terraform/
│   ├── main.tf                 # Main Terraform configuration
│   ├── database.tf             # Cloud SQL configuration
│   ├── storage.tf              # Cloud Storage buckets
│   ├── cache.tf                # Redis configuration
│   ├── spanner.tf              # Cloud Spanner configuration
│   ├── service_accounts.tf     # IAM and service accounts
│   ├── variables.tf            # Variable definitions
│   ├── outputs.tf              # Output values
│   └── terraform.tfvars.example # Example variables file
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud SDK**: Install and configure `gcloud`
2. **Terraform**: Install Terraform >= 1.0
3. **Project Access**: Ensure you have Owner or Editor access to the GCP project

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ArjunSeeramsetty/Validatus2.git
   cd Validatus2
   ```

2. **Configure your project**:
   ```bash
   # Set your project ID
   export PROJECT_ID="your-validatus-project-id"
   
   # Update Terraform files with your project ID
   sed -i "s/validatus-platform/$PROJECT_ID/g" infrastructure/terraform/*.tf
   ```

3. **Run the complete setup**:
   ```bash
   # Make setup script executable
   chmod +x setup-validatus-production.sh
   
   # Run complete setup
   ./setup-validatus-production.sh
   ```

### Manual Setup (Alternative)

If you prefer to run the setup steps manually:

1. **Set up infrastructure**:
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform plan -var="project_id=$PROJECT_ID"
   terraform apply -var="project_id=$PROJECT_ID"
   ```

2. **Set up database**:
   ```bash
   cd ../../backend
   python scripts/setup_database.py
   ```

3. **Deploy application**:
   ```bash
   cd ..
   gcloud builds submit --config=cloudbuild-production.yaml .
   ```

## 🔧 Configuration

### Environment Variables

The infrastructure generates a `.env.production` file with all necessary configuration. Key variables include:

- `GCP_PROJECT_ID`: Your GCP project ID
- `CLOUD_SQL_CONNECTION_NAME`: Cloud SQL connection string
- `CONTENT_STORAGE_BUCKET`: Storage bucket for content
- `REDIS_HOST`: Redis instance host
- `SPANNER_INSTANCE_ID`: Spanner instance for analytics

### Customization

You can customize the infrastructure by:

1. **Editing variables** in `infrastructure/terraform/terraform.tfvars`
2. **Modifying resource configurations** in the respective `.tf` files
3. **Adjusting environment variables** in `backend/env.production.template`

## 💰 Cost Optimization

The infrastructure includes several cost optimization features:

- **Lifecycle policies** for Cloud Storage (Standard → Nearline → Coldline)
- **Processing units** for Spanner (100 PU minimum)
- **Regional deployment** for reduced egress costs
- **Automatic scaling** for Cloud Run services

### Estimated Monthly Costs

- **Cloud SQL** (2 vCPU, 7.5GB): ~$200-300
- **Redis** (4GB, HA): ~$150-200
- **Spanner** (100 PU): ~$100-150
- **Cloud Storage**: ~$20-50 (depending on usage)
- **Cloud Run**: ~$10-50 (depending on traffic)

**Total estimated cost**: ~$480-750/month

## 🔒 Security

The infrastructure implements several security best practices:

- **Private networking** with VPC and Cloud NAT
- **IAM service accounts** with minimal required permissions
- **Secret Manager** for sensitive data (passwords, keys)
- **Encryption at rest** for all storage services
- **Network isolation** between services

## 📊 Monitoring

Built-in monitoring includes:

- **Cloud Logging** for application logs
- **Cloud Monitoring** for metrics and alerts
- **Health checks** for all services
- **Performance monitoring** for databases

## 🚨 Troubleshooting

### Common Issues

1. **Permission errors**: Ensure you have the required IAM roles
2. **API not enabled**: The setup script enables all required APIs automatically
3. **Resource limits**: Check your GCP quotas and limits
4. **Network issues**: Verify VPC and firewall configurations

### Getting Help

1. **Check logs**: Use `gcloud logging` to view application logs
2. **Verify services**: Use the health check endpoints
3. **Test connectivity**: Use the verification scripts
4. **Review Terraform**: Check `terraform plan` for configuration issues

## 🔄 Updates and Maintenance

### Updating Infrastructure

1. **Modify Terraform files** as needed
2. **Run terraform plan** to review changes
3. **Apply changes** with `terraform apply`
4. **Update application** if needed

### Backup and Recovery

- **Cloud SQL**: Automated daily backups with 30-day retention
- **Cloud Storage**: Versioning enabled for all buckets
- **Spanner**: Point-in-time recovery available

## 📚 Additional Resources

- [Terraform GCP Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Validatus Application Documentation](../README.md)

## 🤝 Contributing

When making changes to the infrastructure:

1. **Test locally** with Terraform plan
2. **Use staging environment** for testing
3. **Document changes** in commit messages
4. **Update this README** if needed
5. **Notify team** of breaking changes

---

**Note**: This infrastructure is designed for production use. Ensure you understand the costs and implications before deploying to production.
