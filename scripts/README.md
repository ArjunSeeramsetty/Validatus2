# Validatus2 Scripts Directory

Essential deployment, setup, and verification scripts for the Validatus2 platform.

## 📁 Directory Structure

```
scripts/
├── README.md                                    # This file
├── deploy.sh                                    # Main deployment script
├── setup-gcp-project.sh                         # GCP project initialization
├── setup-terraform-backend.sh                   # Terraform backend setup
├── load-env.sh                                  # Environment loading (Linux/Mac)
└── windows/                                     # Windows-specific scripts
    ├── README.md                                # Windows scripts documentation
    ├── Install-Prerequisites.ps1                # Prerequisites installation
    ├── Setup-GCP-Infrastructure.ps1             # GCP infrastructure setup
    ├── Load-EnvironmentVariables.ps1            # Environment loading
    ├── Check-Deployment-Status.ps1              # Deployment status check
    ├── Verify-Production.ps1                    # Production verification
    └── Test-Complete-Application.ps1            # Complete application testing
```

## 🚀 Quick Start

### Deploy to Production
```bash
# Linux/Mac
./deploy.sh

# Windows
.\deploy.ps1
```

### Complete Setup (First Time)
```bash
# Linux/Mac
./setup-validatus-production.sh

# Windows
.\setup-validatus-production.ps1 -ProjectId validatus-platform
```

## 📜 Script Descriptions

### Deployment Scripts

#### `deploy.sh`
Main deployment script using Google Cloud Build.

**Usage**:
```bash
./deploy.sh
```

**What it does**:
- Enables required GCP APIs
- Builds and deploys backend via Cloud Build
- Builds and deploys frontend via Cloud Build
- Deploys using cloudbuild.yaml configurations

**Prerequisites**:
- gcloud CLI installed and authenticated
- Project ID configured
- cloudbuild.yaml files present

---

### Infrastructure Setup Scripts

#### `setup-gcp-project.sh`
Initializes GCP project with required services and permissions.

**Usage**:
```bash
./scripts/setup-gcp-project.sh
```

**What it does**:
- Enables GCP APIs
- Creates service accounts
- Sets up IAM permissions
- Configures project settings

#### `setup-terraform-backend.sh`
Sets up Terraform backend in Google Cloud Storage.

**Usage**:
```bash
./scripts/setup-terraform-backend.sh
```

**What it does**:
- Creates GCS bucket for Terraform state
- Enables versioning
- Sets up proper permissions

---

### Environment Management

#### `load-env.sh` (Linux/Mac)
Loads environment variables from .env files.

**Usage**:
```bash
source ./scripts/load-env.sh
```

**What it does**:
- Reads .env or env.example
- Exports environment variables
- Validates required variables

---

### Windows Scripts (`windows/`)

See `windows/README.md` for detailed documentation of Windows-specific scripts.

#### Quick Reference:
- **`Install-Prerequisites.ps1`** - Install required software (gcloud, terraform, etc.)
- **`Setup-GCP-Infrastructure.ps1`** - Set up GCP infrastructure
- **`Load-EnvironmentVariables.ps1`** - Load environment variables
- **`Check-Deployment-Status.ps1`** - Check deployment status
- **`Verify-Production.ps1`** - Verify production deployment
- **`Test-Complete-Application.ps1`** - Run comprehensive tests

---

## 🔧 Root-Level Scripts

### `setup-validatus-production.ps1` / `.sh`
Complete production setup orchestrator.

**Usage**:
```bash
# Linux/Mac
./setup-validatus-production.sh

# Windows
.\setup-validatus-production.ps1 -ProjectId validatus-platform
```

**What it does**:
1. Installs prerequisites
2. Sets up GCP infrastructure
3. Configures databases
4. Deploys application
5. Verifies deployment

**Options**:
- `-SkipPrerequisites` - Skip prerequisite installation
- `-SkipInfrastructure` - Skip infrastructure setup
- `-SkipDeployment` - Skip application deployment
- `-AutoApprove` - Auto-approve all steps

### `Setup-Complete-Database.ps1`
Complete database setup for Windows.

**Usage**:
```powershell
.\Setup-Complete-Database.ps1
```

**What it does**:
- Sets up Cloud SQL instance
- Runs database migrations
- Configures database users and permissions
- Creates database schemas

---

## 📝 Script Conventions

### Naming Convention
- **Linux/Mac scripts**: `kebab-case.sh`
- **Windows scripts**: `PascalCase.ps1`
- **Shared names**: Same base name across platforms

### Error Handling
All scripts include:
- `set -e` (bash) or `$ErrorActionPreference = "Stop"` (PowerShell)
- Proper exit codes
- Error messages
- Cleanup on failure

### Logging
- ✅ Success messages in green
- ⚠️ Warnings in yellow
- ❌ Errors in red
- 📝 Info messages in white/cyan

---

## 🧪 Testing

### Run Tests (New Approach)
```bash
# Use pytest instead of script-based tests
pytest tests/ -v

# Specific test categories
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### Application Testing (Windows)
```powershell
.\scripts\windows\Test-Complete-Application.ps1
```

---

## 🆘 Troubleshooting

### Common Issues

#### Permission Denied (Linux/Mac)
```bash
chmod +x scripts/*.sh
chmod +x *.sh
```

#### Execution Policy (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### gcloud Not Authenticated
```bash
gcloud auth login
gcloud auth application-default login
```

#### Environment Variables Not Set
```bash
# Linux/Mac
source ./scripts/load-env.sh

# Windows
.\scripts\windows\Load-EnvironmentVariables.ps1
```

---

## 🔄 Migration from Old Scripts

### Test Scripts → pytest
```bash
# OLD (deleted)
.\test-strategic-analysis-workflow.ps1
.\test-workflow-simple.ps1
./test-strategic-analysis-workflow.sh

# NEW (use pytest)
pytest tests/integration/test_strategic_analysis_workflow.py -v
pytest tests/e2e/test_topic_integration.py -v
```

### Redundant Scripts Removed
25 redundant scripts were removed during consolidation:
- 7 test scripts (replaced by pytest)
- 8 redundant deployment scripts
- 2 redundant infrastructure scripts
- 4 redundant database scripts
- 2 redundant environment scripts
- 2 one-time configuration scripts

See `SCRIPTS_ANALYSIS.md` for full details.

---

## 📚 Related Documentation

- **Tests**: See `tests/README.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`
- **Infrastructure**: See `infrastructure/README.md`
- **Windows Scripts**: See `scripts/windows/README.md`

---

## 🤝 Contributing

When adding new scripts:
1. Follow naming conventions
2. Add comprehensive documentation
3. Include error handling
4. Add to this README
5. Test on both platforms if applicable

---

## 📞 Support

For script-related issues:
- Check script documentation above
- Review error messages
- Consult platform-specific troubleshooting
- Check related documentation files

