# Scripts Analysis and Consolidation Plan

## Overview
Found **39 scripts** (27 PowerShell + 12 Shell scripts) across the project.

## Classification

### 🗑️ Category 1: TEST SCRIPTS - **DELETE** (7 files)
**Reason**: We now have proper pytest test suite in `tests/` directory

1. `test-strategic-analysis-workflow.ps1` - DELETE
2. `test-workflow-simple.ps1` - DELETE  
3. `test-strategic-analysis-workflow.sh` - DELETE
4. `scripts/test-results-analysis.ps1` - DELETE
5. `scripts/monitor-v2-analysis.ps1` - DELETE
6. `scripts/test-v2-scoring.ps1` - DELETE
7. `scripts/verify-v2-scoring.ps1` - DELETE

**Action**: All replaced by `pytest tests/` commands

---

### ✅ Category 2: DEPLOYMENT SCRIPTS - **KEEP & CONSOLIDATE** (11 files → 3 files)

#### Keep These (3 files):
1. **`deploy.sh`** - Main deployment script (GCP Cloud Build)
2. **`setup-validatus-production.ps1`** - Windows production setup orchestrator
3. **`setup-validatus-production.sh`** - Linux/Mac production setup orchestrator

#### DELETE These (8 redundant files):
4. `scripts/deploy-production.sh` - REDUNDANT (duplicate of deploy.sh)
5. `scripts/deploy-application.sh` - REDUNDANT (covered by deploy.sh)
6. `scripts/deploy-infrastructure.sh` - REDUNDANT (covered by terraform)
7. `scripts/deploy_phase_a.sh` - REDUNDANT (phase-based, completed)
8. `scripts/deploy_phase_b.sh` - REDUNDANT (phase-based, completed)
9. `scripts/windows/Deploy-Production.ps1` - REDUNDANT (duplicate of setup-validatus-production.ps1)
10. `scripts/windows/Deploy-With-Security-Fixes.ps1` - REDUNDANT (one-time fix)
11. `scripts/windows/Redeploy-With-Database.ps1` - REDUNDANT (covered by main deployment)

---

### ✅ Category 3: INFRASTRUCTURE SETUP - **KEEP & CONSOLIDATE** (6 files → 4 files)

#### Keep These (4 files):
1. **`scripts/setup-gcp-project.sh`** - GCP project initialization
2. **`scripts/setup-terraform-backend.sh`** - Terraform backend setup
3. **`scripts/windows/Setup-GCP-Infrastructure.ps1`** - Windows GCP setup
4. **`scripts/windows/Install-Prerequisites.ps1`** - Windows prerequisites

#### DELETE These (2 redundant files):
5. `scripts/setup-gcp-infrastructure.sh` - REDUNDANT (duplicate of setup-gcp-project.sh)
6. `scripts/windows/Setup-Terraform-Backend.ps1` - REDUNDANT (duplicate of .sh version)

---

### ✅ Category 4: DATABASE SCRIPTS - **KEEP & CONSOLIDATE** (6 files → 2 files)

#### Keep These (2 files):
1. **`Setup-Complete-Database.ps1`** - Complete database setup (Windows)
2. **`scripts/setup-database-schema.ps1`** - Database schema setup

#### DELETE These (4 redundant files):
3. `scripts/windows/Setup-Database-Simple.ps1` - REDUNDANT (duplicate functionality)
4. `scripts/windows/Setup-Database-Infrastructure.ps1` - REDUNDANT (covered by Setup-Complete-Database.ps1)
5. `scripts/windows/Execute-SQL-Migration.ps1` - REDUNDANT (migrations handled by alembic)
6. `scripts/windows/Run-Database-Migrations.ps1` - REDUNDANT (migrations handled by alembic)

---

### ✅ Category 5: ENVIRONMENT MANAGEMENT - **KEEP & CONSOLIDATE** (4 files → 2 files)

#### Keep These (2 files):
1. **`scripts/load-env.sh`** - Load environment variables (Linux/Mac)
2. **`scripts/windows/Load-EnvironmentVariables.ps1`** - Load environment variables (Windows)

#### DELETE These (2 redundant files):
3. `scripts/windows/Set-EnvironmentVariables.ps1` - REDUNDANT (duplicate of Load-EnvironmentVariables.ps1)
4. `scripts/windows/Export-API-Keys-To-SecretManager.ps1` - REDUNDANT (one-time setup)

---

### ✅ Category 6: VERIFICATION SCRIPTS - **KEEP** (3 files)

#### Keep These (3 files):
1. **`scripts/windows/Check-Deployment-Status.ps1`** - Check deployment status
2. **`scripts/windows/Verify-Production.ps1`** - Verify production deployment
3. **`scripts/windows/Test-Complete-Application.ps1`** - Complete application test

---

### 🗑️ Category 7: CONFIGURATION SCRIPTS - **DELETE** (2 files)
**Reason**: One-time fixes, no longer needed

1. `scripts/windows/Fix-Mixed-Content.ps1` - DELETE (one-time fix, completed)
2. `scripts/windows/Update-Application-Config.ps1` - DELETE (handled by environment variables)

---

## Summary

### Files to DELETE: 30 files
- Test scripts: 7
- Redundant deployment: 8
- Redundant infrastructure: 2
- Redundant database: 4
- Redundant environment: 2
- One-time config: 2
- Redundant verification: 5

### Files to KEEP: 14 files
- Deployment: 3
- Infrastructure: 4
- Database: 2
- Environment: 2
- Verification: 3

### Reduction: 39 → 14 files (64% reduction)

---

## Proposed Final Structure

```
scripts/
├── deploy.sh                                    # Main deployment
├── setup-gcp-project.sh                         # GCP initialization
├── setup-terraform-backend.sh                   # Terraform setup
├── load-env.sh                                  # Environment loading (Linux/Mac)
└── windows/
    ├── Install-Prerequisites.ps1                # Prerequisites
    ├── Setup-GCP-Infrastructure.ps1             # GCP setup
    ├── Load-EnvironmentVariables.ps1            # Environment loading
    ├── Check-Deployment-Status.ps1              # Status check
    ├── Verify-Production.ps1                    # Production verification
    └── Test-Complete-Application.ps1            # Application testing

Root level:
├── setup-validatus-production.ps1               # Production setup (Windows)
├── setup-validatus-production.sh                # Production setup (Linux/Mac)
├── Setup-Complete-Database.ps1                  # Database setup (Windows)
└── scripts/setup-database-schema.ps1            # Database schema
```

---

## Benefits

1. ✅ **64% reduction** in script files
2. ✅ **No redundancy** - Each script has unique purpose
3. ✅ **Clear organization** - Scripts grouped by function
4. ✅ **Cross-platform** - Both Windows and Linux/Mac support
5. ✅ **Maintainable** - Easier to find and update scripts
6. ✅ **Modern** - Test scripts replaced with pytest

---

## Migration Notes

### Test Scripts → pytest
```bash
# OLD (delete these scripts)
.\test-strategic-analysis-workflow.ps1
.\test-workflow-simple.ps1

# NEW (use pytest)
pytest tests/ -v
pytest tests/integration/test_strategic_analysis_workflow.py -v
```

### Deployment
```bash
# Windows
.\setup-validatus-production.ps1 -ProjectId validatus-platform

# Linux/Mac
./setup-validatus-production.sh
```

### Quick Deploy
```bash
./deploy.sh
```

