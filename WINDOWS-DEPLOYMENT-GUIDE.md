# 🚀 Windows Deployment Guide for Validatus

Complete guide for deploying Validatus to Google Cloud Platform on Windows systems using PowerShell.

## 📋 Quick Start (One Command)

```powershell
# 1. Clone the repository
git clone https://github.com/ArjunSeeramsetty/Validatus2.git
cd Validatus2

# 2. Set execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Run complete setup (replace with your project ID)
.\Setup-Validatus-Production.ps1 -ProjectId "your-validatus-project-id" -AutoApprove
```

That's it! The script will handle everything automatically.

## 🎯 What Gets Deployed

### **Infrastructure Components**
- ✅ **Cloud SQL PostgreSQL** - Primary database with high availability
- ✅ **Cloud Storage** - Three buckets for content, embeddings, and reports
- ✅ **Memorystore Redis** - High-availability caching and session management
- ✅ **Cloud Spanner** - Analytics and cross-topic insights
- ✅ **VPC Network** - Private networking with Cloud NAT
- ✅ **Service Accounts** - Secure IAM configuration
- ✅ **Secret Manager** - Secure credential storage

### **Application Features**
- ✅ **Full GCP Database Persistence** - No local storage fallbacks
- ✅ **Production-Ready Configuration** - Scalable and secure
- ✅ **Comprehensive Monitoring** - Health checks and logging
- ✅ **Cost Optimization** - Lifecycle policies and efficient resources
- ✅ **Security Best Practices** - Private networking and IAM

## 🛠️ Prerequisites

### **System Requirements**
- Windows 10/11 or Windows Server 2019/2022
- PowerShell 5.1 or PowerShell Core 7+
- Administrator privileges (for prerequisite installation)
- Active internet connection

### **GCP Requirements**
- Google Cloud Project with billing enabled
- Owner or Editor permissions on the project
- Required APIs will be enabled automatically

## 📁 Script Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `Setup-Validatus-Production.ps1` | **Main Entry Point** | One-command deployment |
| `Install-Prerequisites.ps1` | Install tools | First-time setup |
| `Setup-GCP-Infrastructure.ps1` | Create GCP resources | Infrastructure setup |
| `Deploy-Production.ps1` | Deploy application | Application deployment |
| `Verify-Production.ps1` | Test deployment | Verification and testing |

## 🔧 Step-by-Step Manual Deployment

If you prefer to run steps individually:

### **Step 1: Install Prerequisites**
```powershell
# Run as Administrator
.\scripts\windows\Install-Prerequisites.ps1
```

This installs:
- Google Cloud CLI
- Terraform
- Python 3.11+
- Git
- Docker Desktop
- Chocolatey (package manager)

### **Step 2: Setup GCP Infrastructure**
```powershell
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId "your-project-id" -AutoApprove
```

This creates:
- All GCP services and resources
- Database schemas
- Environment configuration
- Service accounts and permissions

### **Step 3: Deploy Application**
```powershell
.\scripts\windows\Deploy-Production.ps1 -ProjectId "your-project-id"
```

This:
- Builds the application container
- Deploys to Cloud Run
- Tests the deployment
- Sets up monitoring

### **Step 4: Verify Deployment**
```powershell
.\scripts\windows\Verify-Production.ps1 -ProjectId "your-project-id"
```

This runs comprehensive tests:
- Health checks
- API functionality
- Database connectivity
- Performance testing

## 🎛️ Advanced Configuration

### **Custom Project Settings**
```powershell
# Custom region
.\Setup-Validatus-Production.ps1 -ProjectId "your-project" -Region "us-east1"

# Skip specific steps
.\Setup-Validatus-Production.ps1 -ProjectId "your-project" -SkipPrerequisites -SkipInfrastructure
```

### **Environment Variables**
After deployment, you can customize settings in `.env.production`:
```env
# Performance settings
MAX_CONCURRENT_OPERATIONS=100
CONNECTION_POOL_SIZE=30
CACHE_TTL=7200

# Monitoring settings
LOG_LEVEL=DEBUG
ENABLE_TRACING=true
```

## 💰 Cost Estimation

### **Monthly Costs (Approximate)**
- **Cloud SQL** (2 vCPU, 7.5GB): ~$200-300
- **Redis** (4GB, HA): ~$150-200
- **Spanner** (100 PU): ~$100-150
- **Cloud Storage**: ~$20-50 (depending on usage)
- **Cloud Run**: ~$10-50 (depending on traffic)

**Total estimated cost**: ~$480-750/month

### **Cost Optimization Features**
- Automatic storage tiering (Standard → Nearline → Coldline)
- Efficient resource sizing
- Lifecycle policies for data retention
- Monitoring and alerting for cost control

## 🔒 Security Features

### **Network Security**
- Private VPC with no public IPs for databases
- Cloud NAT for outbound internet access
- Firewall rules restricting access

### **Access Control**
- Service accounts with minimal required permissions
- IAM roles for fine-grained access control
- Secret Manager for credential storage

### **Data Protection**
- Encryption at rest for all storage services
- Encryption in transit for all communications
- Backup and disaster recovery capabilities

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Execution Policy Error**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **2. Administrator Privileges Required**
- Run PowerShell as Administrator for prerequisite installation
- Regular user privileges are sufficient for deployment

#### **3. Google Cloud Authentication**
```powershell
# Re-authenticate
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

#### **4. Build Failures**
- Check Cloud Build logs in GCP Console
- Verify all dependencies are installed
- Ensure sufficient project quotas

#### **5. Health Check Failures**
- Check Cloud Run logs
- Verify GCP services are running
- Test database connectivity

### **Debug Mode**
```powershell
# Enable verbose output
$VerbosePreference = "Continue"
.\Setup-Validatus-Production.ps1 -ProjectId "your-project" -Verbose
```

## 📊 Monitoring and Maintenance

### **Health Monitoring**
- **Application Health**: `https://your-service-url/health`
- **GCP Console**: Monitor all services in real-time
- **Logs**: Cloud Logging for detailed application logs

### **Performance Monitoring**
- **Response Times**: Track API performance
- **Resource Usage**: Monitor CPU, memory, and storage
- **Error Rates**: Track application errors and exceptions

### **Maintenance Tasks**
- **Backups**: Automatic daily backups with 30-day retention
- **Updates**: Regular security and feature updates
- **Scaling**: Automatic scaling based on demand

## 🎉 Post-Deployment

### **Your Application URLs**
After successful deployment, you'll have:
- **Application**: `https://your-service-url`
- **Health Check**: `https://your-service-url/health`
- **API Documentation**: `https://your-service-url/docs`
- **GCP Console**: `https://console.cloud.google.com/run`

### **Next Steps**
1. **Test Your Application**: Use the verification script results
2. **Configure Custom Domain**: Set up your own domain (optional)
3. **Set Up Monitoring**: Configure alerts and notifications
4. **Backup Strategy**: Verify backup and recovery procedures
5. **Team Access**: Configure IAM for team members

## 🆘 Getting Help

### **Documentation**
- [Windows Scripts Documentation](scripts/windows/README.md)
- [Infrastructure Documentation](infrastructure/README.md)
- [Application Documentation](README.md)

### **Support Resources**
- Check troubleshooting section above
- Review GCP Console logs
- Verify all prerequisites are installed
- Ensure proper GCP permissions

### **Community**
- GitHub Issues: Report bugs and request features
- Documentation: Contribute improvements
- Examples: Share deployment configurations

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ All verification tests pass
- ✅ Health check returns "healthy" status
- ✅ Topics can be created and retrieved
- ✅ Database connectivity is confirmed
- ✅ Performance meets expectations (< 2s response time)

## 🚀 Ready to Deploy?

Run this command to get started:

```powershell
.\Setup-Validatus-Production.ps1 -ProjectId "your-validatus-project-id" -AutoApprove
```

Your Validatus platform will be fully operational with enterprise-grade GCP persistence!

---

**Need help?** Check the troubleshooting section or review the detailed script documentation in `scripts/windows/README.md`.
