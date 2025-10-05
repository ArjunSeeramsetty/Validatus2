<#
.SYNOPSIS
    Update application configuration for database connectivity
.DESCRIPTION
    This script updates both frontend and backend configurations with database settings
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [string]$BackendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app",
    [string]$FrontendUrl = "https://validatus-frontend-ssivkqhvhq-uc.a.run.app"
)

Write-Host "🔧 Updating Application Configuration..." -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Function to update backend configuration
function Update-BackendConfig {
    Write-Host "📝 Updating backend configuration..." -ForegroundColor Cyan
    
    # Create minimal backend config that works with Cloud SQL
    $backendConfig = @"
"""
Updated backend configuration for production deployment with Cloud SQL
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "Validatus Backend API"
    version: str = "3.1.0"
    environment: str = "production"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # GCP
    gcp_project_id: str = "$($ProjectId.Replace('"', '\"'))"
    gcp_region: str = "us-central1"
    
    # Database
    database_url: Optional[str] = None
    cloud_sql_connection_name: Optional[str] = None
    cloud_sql_database: str = "validatus"
    cloud_sql_user: str = "validatus_app"
    
    # Redis (configure via environment variables for production)
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Features
    local_development_mode: bool = False
    enable_caching: bool = True
    enable_monitoring: bool = True
    
    # CORS
    allowed_origins: List[str] = [
        "$($FrontendUrl.Replace('"', '\"'))",
        "$($BackendUrl.Replace('"', '\"'))"
    ]
    
    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        case_sensitive = True

settings = Settings()
"@

    # Save to backend config file
    $backendConfigPath = "backend\app\core\config.py"
    if (Test-Path $backendConfigPath) {
        # Backup existing config
        Copy-Item $backendConfigPath "${backendConfigPath}.backup"
    }
    
    $backendConfig | Out-File -FilePath $backendConfigPath -Encoding utf8
    Write-Host "✅ Backend configuration updated" -ForegroundColor Green
}

# Function to update frontend configuration
function Update-FrontendConfig {
    Write-Host "📝 Updating frontend configuration..." -ForegroundColor Cyan
    
    # Create/update frontend environment config
    $frontendEnv = @"
# Frontend Environment Configuration
REACT_APP_API_BASE_URL=$BackendUrl
REACT_APP_PROJECT_ID=$ProjectId
REACT_APP_ENVIRONMENT=production
"@

    $frontendEnvPath = "frontend\.env.production"
    $frontendEnv | Out-File -FilePath $frontendEnvPath -Encoding utf8
    
    # Update the main config file
    $frontendConfig = @"
// Frontend API configuration
const API_CONFIG = {
  BASE_URL: '$($BackendUrl.Replace("'", "\'"))',
  ENDPOINTS: {
    HEALTH: '/health',
    TOPICS: '/api/v3/topics',
    CREATE_TOPIC: '/api/v3/topics/create'
  }
};

export default API_CONFIG;
"@

    $frontendConfigPath = "frontend\src\config\api.js"
    $frontendConfigDir = Split-Path $frontendConfigPath
    
    if (-not (Test-Path $frontendConfigDir)) {
        New-Item -ItemType Directory -Path $frontendConfigDir -Force
    }
    
    $frontendConfig | Out-File -FilePath $frontendConfigPath -Encoding utf8
    
    Write-Host "✅ Frontend configuration updated" -ForegroundColor Green
}

# Function to update main application environment
function Update-MainEnvironment {
    Write-Host "📝 Updating main environment configuration..." -ForegroundColor Cyan
    
    # Read the production environment if it exists
    $prodEnvPath = ".env.production"
    $baseConfig = @{}
    
    if (Test-Path $prodEnvPath) {
        $prodContent = Get-Content $prodEnvPath
        foreach ($line in $prodContent) {
            if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
                $parts = $line.Split("=", 2)
                if ($parts.Length -eq 2) {
                    $baseConfig[$parts[0].Trim()] = $parts[1].Trim()
                }
            }
        }
    }
    
    # Update with application URLs
    $baseConfig["FRONTEND_URL"] = $FrontendUrl
    $baseConfig["BACKEND_URL"] = $BackendUrl
    $baseConfig["ALLOWED_ORIGINS"] = "$FrontendUrl,$BackendUrl"
    
    # Build updated environment content
    $envContent = "# Updated Validatus Environment Configuration`n"
    $envContent += "# Generated on: $(Get-Date)`n`n"
    
    foreach ($key in $baseConfig.Keys | Sort-Object) {
        $envContent += "$key=$($baseConfig[$key])`n"
    }
    
    $envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline
    $envContent | Out-File -FilePath $prodEnvPath -Encoding utf8 -NoNewline
    
    Write-Host "✅ Main environment configuration updated" -ForegroundColor Green
}

# Function to create deployment configuration
function New-DeploymentConfig {
    Write-Host "📝 Creating deployment configuration..." -ForegroundColor Cyan
    
    # Create Cloud Build configuration for redeployment
    $cloudBuildConfig = @"
steps:
  # Build and deploy backend
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-f'
      - 'backend/Dockerfile'
      - '-t'
      - 'gcr.io/$PROJECT_ID/validatus-backend:latest'
      - 'backend'
    timeout: '1200s'

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/validatus-backend:latest']

  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'validatus-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/validatus-backend:latest'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'GCP_PROJECT_ID=$PROJECT_ID,DATABASE_URL=$${_DATABASE_URL},FRONTEND_URL=$FrontendUrl'

  # Build and deploy frontend
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-f'
      - 'frontend/Dockerfile'
      - '-t'
      - 'gcr.io/$PROJECT_ID/validatus-frontend:latest'
      - 'frontend'
    timeout: '600s'

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/validatus-frontend:latest']

  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'validatus-frontend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/validatus-frontend:latest'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'REACT_APP_API_BASE_URL=$BackendUrl'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

substitutions:
  _DATABASE_URL: 'postgresql://user:pass@/cloudsql/connection'  # Update with actual value

timeout: '2400s'
"@

    $cloudBuildConfig | Out-File -FilePath "cloudbuild-update.yaml" -Encoding utf8
    Write-Host "✅ Deployment configuration created: cloudbuild-update.yaml" -ForegroundColor Green
}

# Validate ProjectId to prevent injection attacks
function Test-ProjectId {
    param([string]$ProjectId)
    
    # Project IDs should be alphanumeric with hyphens only
    if ($ProjectId -notmatch '^[a-z][a-z0-9-]*[a-z0-9]$' -and $ProjectId.Length -gt 6 -and $ProjectId.Length -lt 64) {
        throw "Invalid Project ID format. Project IDs must be lowercase alphanumeric with hyphens, 6-63 characters long, starting and ending with alphanumeric characters."
    }
    
    # Check for dangerous characters
    if ($ProjectId -match '["''<>{}|\\`$]') {
        throw "Project ID contains dangerous characters that could cause injection attacks."
    }
    
    return $true
}

# Main execution
try {
    # Validate inputs
    Test-ProjectId $ProjectId
    
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Backend URL: $BackendUrl" -ForegroundColor White
    Write-Host "Frontend URL: $FrontendUrl" -ForegroundColor White
    Write-Host ""
    
    Update-BackendConfig
    Update-FrontendConfig
    Update-MainEnvironment
    New-DeploymentConfig
    
    Write-Host ""
    Write-Host "🎉 Application configuration updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Updated Files:" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    Write-Host "✅ backend\app\core\config.py" -ForegroundColor White
    Write-Host "✅ frontend\.env.production" -ForegroundColor White
    Write-Host "✅ frontend\src\config\api.js" -ForegroundColor White
    Write-Host "✅ .env.production" -ForegroundColor White
    Write-Host "✅ cloudbuild-update.yaml" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Run: .\scripts\windows\Redeploy-With-Database.ps1" -ForegroundColor White
    Write-Host "2. Test the updated application" -ForegroundColor White
    
} catch {
    Write-Host "❌ Configuration update failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
