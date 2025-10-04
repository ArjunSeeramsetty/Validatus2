# Windows PowerShell Deployment Scripts for Validatus

This directory contains comprehensive PowerShell scripts for deploying Validatus to Google Cloud Platform on Windows systems.

## 📁 Script Overview

| Script | Purpose | Description |
|--------|---------|-------------|
| `Install-Prerequisites.ps1` | Prerequisites Installation | Installs all required tools (Python, gcloud, Terraform, etc.) |
| `Setup-GCP-Infrastructure.ps1` | Infrastructure Setup | Creates all GCP resources using Terraform |
| `Deploy-Production.ps1` | Application Deployment | Builds and deploys the application to Cloud Run |
| `Verify-Production.ps1` | Deployment Verification | Tests the deployed application thoroughly |
| `Set-EnvironmentVariables.ps1` | Environment Setup | Sets up environment variables for local development |

## 🚀 Quick Start

### **One-Command Deployment**

```powershell
# Clone the repository
git clone https://github.com/ArjunSeeramsetty/Validatus2.git
cd Validatus2

# Set execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run complete setup (replace with your project ID)
.\Setup-Validatus-Production.ps1 -ProjectId "your-validatus-project-id" -AutoApprove
```

### **Step-by-Step Deployment**

```powershell
# 1. Install prerequisites (run as Administrator)
.\scripts\windows\Install-Prerequisites.ps1

# 2. Setup GCP infrastructure
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId "your-project-id" -AutoApprove

# 3. Deploy application
.\scripts\windows\Deploy-Production.ps1 -ProjectId "your-project-id"

# 4. Verify deployment
.\scripts\windows\Verify-Production.ps1 -ProjectId "your-project-id"
```

## 🔧 Prerequisites

### **System Requirements**
- Windows 10/11 or Windows Server 2019/2022
- PowerShell 5.1 or PowerShell Core 7+
- Administrator privileges (for prerequisite installation)

### **Manual Prerequisites (if not using Install-Prerequisites.ps1)**
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://www.terraform.io/downloads)
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/download/win)
- [Chocolatey](https://chocolatey.org/install) (for automated installation)

### **GCP Requirements**
- Active Google Cloud Project with billing enabled
- Owner or Editor permissions on the project
- Required APIs enabled (handled automatically by scripts)

## 📋 Detailed Script Usage

### **1. Install-Prerequisites.ps1**

Installs all required tools for Validatus deployment.

```powershell
# Install all prerequisites
.\scripts\windows\Install-Prerequisites.ps1

# Skip specific tools
.\scripts\windows\Install-Prerequisites.ps1 -SkipPython -SkipTerraform
```

**Features:**
- Automatic Chocolatey installation
- Python 3.11+ installation
- Google Cloud CLI installation
- Terraform installation
- Git and Docker Desktop installation
- Comprehensive verification

### **2. Setup-GCP-Infrastructure.ps1**

Sets up all GCP infrastructure using Terraform.

```powershell
# Basic setup
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId "your-project-id"

# With custom region
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId "your-project-id" -Region "us-east1"

# Skip planning phase
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId "your-project-id" -SkipPlan

# Auto-approve all prompts
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId "your-project-id" -AutoApprove
```

**Features:**
- Google Cloud authentication setup
- Terraform initialization and validation
- Infrastructure deployment with confirmation
- Environment configuration generation
- Database schema setup
- Deployment verification

### **3. Deploy-Production.ps1**

Builds and deploys the application to Cloud Run.

```powershell
# Basic deployment
.\scripts\windows\Deploy-Production.ps1 -ProjectId "your-project-id"

# Custom service name and region
.\scripts\windows\Deploy-Production.ps1 -ProjectId "your-project-id" -ServiceName "my-backend" -Region "us-east1"

# Skip build step
.\scripts\windows\Deploy-Production.ps1 -ProjectId "your-project-id" -SkipBuild

# Skip tests
.\scripts\windows\Deploy-Production.ps1 -ProjectId "your-project-id" -SkipTests

# Custom timeout
.\scripts\windows\Deploy-Production.ps1 -ProjectId "your-project-id" -TimeoutMinutes 60
```

**Features:**
- Cloud Build integration
- Health check with retry logic
- Database connectivity testing
- Monitoring setup
- Post-deployment verification

### **4. Verify-Production.ps1**

Comprehensive verification of the deployed application.

```powershell
# Basic verification
.\scripts\windows\Verify-Production.ps1 -ProjectId "your-project-id"

# Skip API tests
.\scripts\windows\Verify-Production.ps1 -ProjectId "your-project-id" -SkipApiTests

# Verbose output
.\scripts\windows\Verify-Production.ps1 -ProjectId "your-project-id" -Verbose

# Custom service URL
.\scripts\windows\Verify-Production.ps1 -BaseUrl "https://your-custom-url.com"
```

**Features:**
- Health endpoint testing
- Topic creation and retrieval testing
- Database connectivity verification
- Performance testing
- Comprehensive reporting

### **5. Set-EnvironmentVariables.ps1**

Sets up environment variables for local development.

```powershell
# Use default .env.production file
.\scripts\windows\Set-EnvironmentVariables.ps1

# Use custom environment file
.\scripts\windows\Set-EnvironmentVariables.ps1 -EnvFile ".env.local"
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. Execution Policy Errors**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **2. Administrator Privileges Required**
- Run PowerShell as Administrator for prerequisite installation
- Regular user privileges are sufficient for deployment scripts

#### **3. Google Cloud Authentication Issues**
```powershell
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

#### **4. Terraform State Issues**
```powershell
# Reinitialize Terraform
cd infrastructure\terraform
terraform init
```

#### **5. Python Virtual Environment Issues**
```powershell
# Recreate virtual environment
cd backend
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-gcp.txt
```

### **Debugging Tips**

1. **Enable Verbose Output:**
   ```powershell
   $VerbosePreference = "Continue"
   .\script-name.ps1 -Verbose
   ```

2. **Check Script Execution:**
   ```powershell
   # Check if scripts exist
   Test-Path ".\scripts\windows\*.ps1"
   ```

3. **Verify Dependencies:**
   ```powershell
   # Check if tools are available
   gcloud version
   terraform version
   python --version
   ```

4. **Review Logs:**
   - Check PowerShell console output
   - Review Cloud Build logs in GCP Console
   - Check Cloud Run logs for application issues

## 🔒 Security Considerations

### **Service Account Permissions**
The scripts create a service account with minimal required permissions:
- Cloud SQL Client
- Storage Object Admin
- Redis Editor
- Spanner Database User
- AI Platform User
- Secret Manager Secret Accessor

### **Network Security**
- Private VPC with Cloud NAT
- No public IP addresses for databases
- Secure inter-service communication

### **Secrets Management**
- Database passwords stored in Secret Manager
- Service account keys managed securely
- No hardcoded credentials

## 📊 Cost Optimization

### **Resource Sizing**
- Cloud SQL: 2 vCPU, 7.5GB RAM (adjustable)
- Redis: 4GB memory (adjustable)
- Spanner: 100 processing units (adjustable)

### **Lifecycle Policies**
- Cloud Storage: Automatic tiering (Standard → Nearline → Coldline)
- Automatic backup retention
- Cost monitoring and alerts

## 🚀 Advanced Usage

### **Custom Configuration**
1. Edit `infrastructure/terraform/terraform.tfvars` for custom settings
2. Modify environment variables in generated `.env.production`
3. Adjust resource sizes in Terraform files

### **Multi-Environment Deployment**
```powershell
# Development environment
.\Setup-Validatus-Production.ps1 -ProjectId "validatus-dev" -Region "us-central1"

# Staging environment  
.\Setup-Validatus-Production.ps1 -ProjectId "validatus-staging" -Region "us-east1"

# Production environment
.\Setup-Validatus-Production.ps1 -ProjectId "validatus-prod" -Region "us-central1"
```

### **CI/CD Integration**
The scripts can be integrated into CI/CD pipelines:
```yaml
# GitHub Actions example
- name: Deploy to GCP
  run: |
    .\Setup-Validatus-Production.ps1 -ProjectId ${{ secrets.GCP_PROJECT_ID }} -AutoApprove
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GCP Console logs
3. Verify all prerequisites are installed
4. Ensure proper GCP permissions

## 📚 Additional Resources

- [Google Cloud SDK Documentation](https://cloud.google.com/sdk/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Validatus Application Documentation](../README.md)
