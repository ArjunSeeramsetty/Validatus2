# ⚡ Quick Start - Deploy Validatus in 5 Minutes

Get Validatus running on GCP with full database persistence in just a few commands!

## 🚀 One-Command Deployment

### **Windows Users**
```powershell
# 1. Clone and setup
git clone https://github.com/ArjunSeeramsetty/Validatus2.git
cd Validatus2

# 2. Run deployment (replace with your project ID)
.\Setup-Validatus-Production.ps1 -ProjectId "your-project-id" -AutoApprove
```

### **Linux/Mac Users**
```bash
# 1. Clone and setup
git clone https://github.com/ArjunSeeramsetty/Validatus2.git
cd Validatus2

# 2. Run deployment (replace with your project ID)
chmod +x setup-validatus-production.sh
./setup-validatus-production.sh
```

## 📋 Prerequisites (2 minutes)

### **What You Need**
- ✅ Google Cloud Project with billing enabled
- ✅ Owner/Editor permissions on the project
- ✅ Windows 10/11, macOS, or Linux
- ✅ Internet connection

### **What Gets Installed Automatically**
- ✅ Google Cloud CLI
- ✅ Terraform
- ✅ Python 3.11+
- ✅ Git
- ✅ All required dependencies

## 🎯 What Happens During Deployment

### **Phase 1: Infrastructure Setup (3-5 minutes)**
- Creates VPC network with private subnets
- Sets up Cloud SQL PostgreSQL database
- Creates Cloud Storage buckets
- Configures Redis cache
- Sets up Cloud Spanner analytics
- Creates service accounts and permissions

### **Phase 2: Application Deployment (2-3 minutes)**
- Builds application container
- Deploys to Cloud Run
- Configures environment variables
- Sets up database schemas
- Tests all connections

### **Phase 3: Verification (1 minute)**
- Tests health endpoints
- Verifies database connectivity
- Tests API functionality
- Checks performance

## 🎉 Success! Your Application Is Ready

After deployment, you'll have:

### **Application URLs**
- **Main Application**: `https://validatus-backend-[hash]-uc.a.run.app`
- **Health Check**: `https://validatus-backend-[hash]-uc.a.run.app/health`
- **API Documentation**: `https://validatus-backend-[hash]-uc.a.run.app/docs`

### **GCP Console Access**
- **Cloud Run**: Monitor your application
- **Cloud SQL**: Manage your database
- **Cloud Storage**: View your data buckets
- **Monitoring**: Track performance and logs

## 🧪 Test Your Deployment

### **Quick Health Check**
```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe validatus-backend --region=us-central1 --format="value(status.url)")

# Test health endpoint
curl $SERVICE_URL/health
```

### **Test Topic Creation**
```bash
# Create a test topic
curl -X POST $SERVICE_URL/api/v3/topics/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Topic",
    "description": "Quick start test",
    "analysis_type": "comprehensive",
    "user_id": "test_user"
  }'
```

### **Check Topics**
```bash
# List all topics
curl $SERVICE_URL/api/v3/topics
```

## 💰 Cost Overview

### **Estimated Monthly Costs**
- **Cloud SQL** (2 vCPU, 7.5GB): ~$200-300
- **Redis** (4GB, HA): ~$150-200
- **Spanner** (100 PU): ~$100-150
- **Storage**: ~$20-50
- **Cloud Run**: ~$10-50
- **Total**: ~$480-750/month

### **Free Tier Benefits**
- Cloud Run: 2 million requests/month free
- Cloud Storage: 5GB free
- Cloud SQL: Free tier available (smaller instance)

## 🔧 Customization Options

### **Adjust Resource Sizes**
Edit `infrastructure/terraform/variables.tf`:
```hcl
variable "db_instance_tier" {
  default = "db-f1-micro"  # Smaller for testing
}

variable "redis_memory_size" {
  default = 1  # 1GB for testing
}
```

### **Change Region**
```powershell
# Windows
.\Setup-Validatus-Production.ps1 -ProjectId "your-project" -Region "us-east1"

# Linux/Mac
./setup-validatus-production.sh
```

## 🚨 Troubleshooting

### **Common Issues & Quick Fixes**

#### **1. "gcloud not found"**
```bash
# Reinstall Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

#### **2. "Permission denied"**
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

#### **3. "Billing not enabled"**
- Go to [GCP Console](https://console.cloud.google.com/billing)
- Enable billing for your project

#### **4. "Build timeout"**
```bash
# Increase timeout
gcloud builds submit --timeout=3600s .
```

### **Check Deployment Status**
```powershell
# Windows
.\scripts\windows\Check-Deployment-Status.ps1 -ProjectId "your-project"

# Linux/Mac
python scripts/verify-production.py
```

## 🎯 Next Steps

### **Immediate Actions**
1. **Test your application** - Create topics and verify persistence
2. **Check monitoring** - Review logs and metrics in GCP Console
3. **Configure domain** - Set up custom domain (optional)

### **Optional Enhancements**
1. **Set up alerts** - Configure monitoring alerts
2. **Backup strategy** - Verify backup schedules
3. **Team access** - Add team members to GCP project
4. **Custom branding** - Update frontend with your branding

## 📚 Documentation

### **Detailed Guides**
- [Windows Deployment Guide](WINDOWS-DEPLOYMENT-GUIDE.md) - Complete Windows instructions
- [Infrastructure Documentation](infrastructure/README.md) - Terraform and GCP setup
- [Deployment Complete Guide](DEPLOYMENT-COMPLETE.md) - Full implementation details

### **Script Documentation**
- [Windows Scripts](scripts/windows/README.md) - PowerShell script details
- [API Documentation](backend/README.md) - Backend API reference

## 🎉 You're Done!

Your Validatus platform is now running on GCP with:
- ✅ Full database persistence
- ✅ Scalable architecture
- ✅ Production-ready security
- ✅ Comprehensive monitoring
- ✅ Cost optimization

**Start using your application immediately!**

---

**Need help?** Check the troubleshooting section or review the detailed documentation above.
