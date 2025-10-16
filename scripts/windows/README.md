# Windows Scripts for Validatus2

PowerShell scripts for Windows-based development and deployment.

## 📜 Available Scripts

### 1. Install-Prerequisites.ps1
Installs required software for Validatus2 development.

**Usage**:
```powershell
.\scripts\windows\Install-Prerequisites.ps1
```

**What it installs**:
- Google Cloud SDK (gcloud CLI)
- Terraform
- Node.js and npm
- Python 3.10+
- Git (if not present)
- Docker Desktop (optional)

**Options**:
- `-SkipDocker` - Skip Docker installation
- `-SkipPython` - Skip Python installation
- `-Force` - Force reinstall even if present

---

### 2. Setup-GCP-Infrastructure.ps1
Sets up Google Cloud Platform infrastructure.

**Usage**:
```powershell
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId validatus-platform
```

**What it does**:
- Enables required GCP APIs
- Creates service accounts
- Sets up IAM roles
- Configures Cloud SQL
- Sets up Secret Manager
- Creates storage buckets

**Required Parameters**:
- `-ProjectId` - GCP project ID

**Optional Parameters**:
- `-Region` - GCP region (default: us-central1)
- `-SkipCloudSQL` - Skip Cloud SQL setup
- `-SkipSecrets` - Skip Secret Manager setup

---

### 3. Load-EnvironmentVariables.ps1
Loads environment variables from .env files.

**Usage**:
```powershell
.\scripts\windows\Load-EnvironmentVariables.ps1
```

**What it does**:
- Reads `.env` file
- Exports variables to current session
- Validates required variables
- Optionally persists to user environment

**Options**:
- `-EnvFile` - Path to .env file (default: .env)
- `-Persist` - Save to user environment variables
- `-Validate` - Validate required variables exist

---

### 4. Check-Deployment-Status.ps1
Checks the status of deployed services.

**Usage**:
```powershell
.\scripts\windows\Check-Deployment-Status.ps1
```

**What it checks**:
- Backend Cloud Run service status
- Frontend Cloud Run service status
- Cloud SQL instance status
- Service endpoints availability
- Health check endpoints

**Output**:
- Service URLs
- Health status
- Last deployment time
- Version information

---

### 5. Verify-Production.ps1
Comprehensive production deployment verification.

**Usage**:
```powershell
.\scripts\windows\Verify-Production.ps1 -ProjectId validatus-platform
```

**What it verifies**:
- All GCP services are running
- Endpoints are accessible
- Health checks pass
- Database connectivity
- API functionality
- Frontend accessibility

**Parameters**:
- `-ProjectId` - GCP project ID
- `-BackendUrl` - Backend URL (optional, auto-detected)
- `-FrontendUrl` - Frontend URL (optional, auto-detected)
- `-Detailed` - Run detailed verification

---

### 6. Test-Complete-Application.ps1
Runs comprehensive application tests.

**Usage**:
```powershell
.\scripts\windows\Test-Complete-Application.ps1
```

**What it tests**:
- API endpoints
- Database connectivity
- Frontend functionality
- Authentication flows
- Core workflows
- Integration points

**Equivalent to**:
```bash
pytest tests/ -v --cov=backend/app
```

**Note**: This script calls pytest. For more granular testing, use pytest directly:
```powershell
# API tests only
pytest tests/api/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v
```

---

## 🚀 Complete Setup Workflow

### First-Time Setup
```powershell
# 1. Install prerequisites
.\scripts\windows\Install-Prerequisites.ps1

# 2. Load environment variables
.\scripts\windows\Load-EnvironmentVariables.ps1 -Persist

# 3. Setup GCP infrastructure
.\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId validatus-platform

# 4. Or use the orchestrator script
.\setup-validatus-production.ps1 -ProjectId validatus-platform
```

### Deployment Verification
```powershell
# 1. Check deployment status
.\scripts\windows\Check-Deployment-Status.ps1

# 2. Verify production
.\scripts\windows\Verify-Production.ps1 -ProjectId validatus-platform

# 3. Run tests
.\scripts\windows\Test-Complete-Application.ps1
```

### Daily Development
```powershell
# Load environment variables
.\scripts\windows\Load-EnvironmentVariables.ps1

# Run local backend
python backend\start_local_backend.py

# Run local frontend (separate terminal)
cd frontend
npm run dev

# Run tests
pytest tests/ -v
```

---

## 🛠️ Prerequisites

Before running these scripts:

1. **PowerShell 5.1+** (Windows 10/11 includes this)
2. **Administrator privileges** (for some installations)
3. **Internet connection** (for downloads)
4. **GCP Account** (for cloud deployments)

### Check PowerShell Version
```powershell
$PSVersionTable.PSVersion
```

### Enable Script Execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎨 Script Features

### Common Features
All Windows scripts include:
- ✅ **Parameter validation**
- ✅ **Colored output** (success/warning/error)
- ✅ **Error handling** with proper exit codes
- ✅ **Progress indicators**
- ✅ **Logging** to console and optionally to file
- ✅ **Help documentation** (use `-Help` or `Get-Help .\script.ps1`)

### Error Handling
```powershell
$ErrorActionPreference = "Stop"

try {
    # Script logic
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
```

### Colored Output
- 🟢 **Green**: Success messages
- 🟡 **Yellow**: Warnings
- 🔴 **Red**: Errors
- 🔵 **Cyan**: Information
- ⚪ **White**: Standard output

---

## 📝 Script Parameters

### Common Parameters
Most scripts support:
- `-Verbose` - Detailed output
- `-WhatIf` - Show what would happen (dry run)
- `-Confirm` - Prompt before making changes
- `-Help` - Display help information

### Example
```powershell
# Verbose output
.\Setup-GCP-Infrastructure.ps1 -ProjectId validatus-platform -Verbose

# Dry run
.\Verify-Production.ps1 -ProjectId validatus-platform -WhatIf

# With confirmation
.\Load-EnvironmentVariables.ps1 -Persist -Confirm
```

---

## 🐛 Troubleshooting

### "Script cannot be loaded" Error
```powershell
# Solution: Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Access Denied" Error
```powershell
# Solution: Run as Administrator
# Right-click PowerShell → "Run as Administrator"
```

### gcloud Command Not Found
```powershell
# Solution 1: Run Install-Prerequisites.ps1
.\scripts\windows\Install-Prerequisites.ps1

# Solution 2: Add to PATH manually
$env:Path += ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
```

### Environment Variables Not Persisting
```powershell
# Solution: Use -Persist flag
.\scripts\windows\Load-EnvironmentVariables.ps1 -Persist
```

### Python Virtual Environment Issues
```powershell
# Activate virtual environment first
.\validatus-env\Scripts\Activate.ps1

# If activation fails, recreate venv
python -m venv validatus-env
.\validatus-env\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

---

## 🔗 Related Documentation

- **Main Scripts README**: `scripts/README.md`
- **Testing Guide**: `tests/README.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Development Guide**: `DEVELOPMENT_HISTORY.md`

---

## 📞 Getting Help

### For Individual Scripts
```powershell
Get-Help .\Setup-GCP-Infrastructure.ps1 -Full
Get-Help .\Verify-Production.ps1 -Examples
```

### For General Issues
1. Check this README
2. Review script output and error messages
3. Check related documentation
4. Review GCP Console for cloud-specific issues
5. Check logs in Cloud Logging

---

## 🤝 Contributing

When adding new Windows scripts:
1. Use **PascalCase** naming (e.g., `My-New-Script.ps1`)
2. Include **parameter validation** and help
3. Use **colored output** for better UX
4. Add **comprehensive error handling**
5. Document in this README
6. Test on Windows 10 and 11
7. Consider adding Linux/Mac equivalent

---

## 📊 Script Dependencies

```
Install-Prerequisites.ps1
    └── (No dependencies)

Setup-GCP-Infrastructure.ps1
    ├── Requires: gcloud CLI
    └── Requires: Project ID

Load-EnvironmentVariables.ps1
    └── Requires: .env file

Check-Deployment-Status.ps1
    ├── Requires: gcloud CLI
    └── Requires: Deployed services

Verify-Production.ps1
    ├── Requires: gcloud CLI
    ├── Requires: curl or Invoke-WebRequest
    └── Depends on: Check-Deployment-Status.ps1

Test-Complete-Application.ps1
    ├── Requires: Python 3.10+
    ├── Requires: pytest
    └── Requires: Backend dependencies
```

---

## 🎓 PowerShell Best Practices

These scripts follow PowerShell best practices:
- ✅ Approved verbs (Get, Set, New, etc.)
- ✅ CmdletBinding for advanced functions
- ✅ Parameter validation
- ✅ Help documentation
- ✅ WhatIf and Confirm support
- ✅ Error handling
- ✅ Consistent naming
- ✅ Meaningful output

---

**Last Updated**: October 16, 2025
**Maintained By**: Validatus2 Development Team
