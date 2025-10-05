<#
.SYNOPSIS
    Deploy Validatus with comprehensive security fixes and multi-region support
.DESCRIPTION
    This script implements all CodeRabbit security recommendations:
    - Uses Secret Manager for DATABASE_URL
    - Dynamic URL resolution for multi-region deployments
    - Backup mechanisms for critical files
    - Enhanced error handling and validation
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$SkipTests
)

Write-Host "🔒 Deploying Validatus with Security Fixes..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Function to validate prerequisites
function Test-Prerequisites {
    Write-Host "🔍 Validating prerequisites..." -ForegroundColor Cyan
    
    # Check if gcloud is authenticated
    try {
        $currentProject = gcloud config get-value project 2>$null
        if ([string]::IsNullOrWhiteSpace($currentProject)) {
            throw "gcloud not authenticated"
        }
        Write-Host "✅ gcloud authenticated (current project: $currentProject)" -ForegroundColor Green
    } catch {
        Write-Host "❌ gcloud authentication required" -ForegroundColor Red
        throw "Please run 'gcloud auth login' and 'gcloud config set project $ProjectId'"
    }
    
    # Check if required APIs are enabled
    $requiredApis = @(
        "cloudbuild.googleapis.com",
        "run.googleapis.com",
        "secretmanager.googleapis.com",
        "sqladmin.googleapis.com"
    )
    
    foreach ($api in $requiredApis) {
        try {
            $enabled = gcloud services list --enabled --filter="name:$api" --format="value(name)" --project=$ProjectId
            if ([string]::IsNullOrWhiteSpace($enabled)) {
                Write-Host "⚠️ Enabling required API: $api" -ForegroundColor Yellow
                gcloud services enable $api --project=$ProjectId
            } else {
                Write-Host "✅ API enabled: $api" -ForegroundColor Green
            }
        } catch {
            Write-Host "❌ Failed to enable API $api" -ForegroundColor Red
            throw
        }
    }
}

# Function to get database URL with validation
function Get-DatabaseURL {
    Write-Host "🔍 Getting database connection details..." -ForegroundColor Cyan
    
    try {
        $connectionName = gcloud sql instances describe validatus-primary --format="value(connectionName)" --project=$ProjectId
        $password = gcloud secrets versions access latest --secret="cloud-sql-password" --project=$ProjectId
        
        # Validate retrieved credentials before constructing the connection string
        if ([string]::IsNullOrWhiteSpace($connectionName)) {
            throw "Failed to retrieve Cloud SQL connection name"
        }
        if ([string]::IsNullOrWhiteSpace($password)) {
            throw "Failed to retrieve database password from secrets"
        }
        
        $databaseUrl = "postgresql+asyncpg://validatus_app:$password@/validatus?host=/cloudsql/$connectionName"
        
        Write-Host "✅ Database connection details retrieved and validated" -ForegroundColor Green
        return $databaseUrl
    } catch {
        Write-Host "❌ Failed to get database connection details: $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
}

# Function to backup critical files
function Backup-CriticalFiles {
    Write-Host "📋 Creating backups of critical files..." -ForegroundColor Cyan
    
    $backups = @{
        "backend\requirements.txt" = "backend\requirements.txt.backup"
        "backend\Dockerfile" = "backend\Dockerfile.backup"
        "frontend\Dockerfile" = "frontend\Dockerfile.backup"
        "cloudbuild.yaml" = "cloudbuild.yaml.backup"
    }
    
    foreach ($original in $backups.Keys) {
        if (Test-Path $original) {
            Copy-Item $original $backups[$original] -Force
            Write-Host "✅ Backed up: $original" -ForegroundColor Green
        }
    }
}

# Function to deploy backend with security fixes
function Deploy-BackendSecure {
    param([string]$DatabaseUrl)
    
    if ($SkipBackend) {
        Write-Host "⏭️ Skipping backend deployment" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🔨 Deploying backend with security fixes..." -ForegroundColor Cyan
    
    # Backup requirements.txt
    $backupPath = "backend\requirements.txt.backup"
    if (Test-Path "backend\requirements.txt") {
        Copy-Item "backend\requirements.txt" $backupPath -Force
        Write-Host "📋 Backed up existing requirements.txt" -ForegroundColor Gray
    }
    
    # Create updated requirements for backend
    $backendReqs = @"
# Minimal production requirements with database connectivity
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.9.2
pydantic-settings==2.1.0
sqlalchemy==2.0.23
alembic==1.13.1
asyncpg==0.29.0
psycopg2-binary==2.9.7
redis==5.0.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
python-dotenv==1.1.1
httpx==0.28.1
requests==2.31.0
google-cloud-secret-manager==2.16.4
google-auth==2.35.0
"@

    $backendReqs | Out-File -FilePath "backend\requirements.txt" -Encoding utf8
    
    # Build backend with region parameter
    Write-Host "🏗️ Building backend..." -ForegroundColor Gray
    gcloud builds submit backend `
        --tag gcr.io/$ProjectId/validatus-backend:secure `
        --project=$ProjectId `
        --region=$Region `
        --timeout=1200s
    
    if ($LASTEXITCODE -ne 0) {
        throw "Backend build failed"
    }
    
    # Store DATABASE_URL in Secret Manager for security
    Write-Host "🔐 Storing DATABASE_URL in Secret Manager..." -ForegroundColor Cyan
    try {
        # Create or update the secret
        $databaseUrl | gcloud secrets create cloud-sql-database-url --data-file=- --project=$ProjectId 2>$null
        if ($LASTEXITCODE -ne 0) {
            # Secret might already exist, update it
            $databaseUrl | gcloud secrets versions add cloud-sql-database-url --data-file=- --project=$ProjectId
        }
        Write-Host "✅ DATABASE_URL stored securely in Secret Manager" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Failed to store DATABASE_URL in Secret Manager: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Deploy to Cloud Run with secrets instead of plain text environment variables
    Write-Host "🚀 Deploying backend to Cloud Run..." -ForegroundColor Gray
    gcloud run deploy validatus-backend `
        --image gcr.io/$ProjectId/validatus-backend:secure `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --memory 1Gi `
        --cpu 1 `
        --timeout 900 `
        --max-instances 10 `
        --set-env-vars "GCP_PROJECT_ID=$ProjectId,ENVIRONMENT=production" `
        --update-secrets "DATABASE_URL=cloud-sql-database-url:latest" `
        --project=$ProjectId
    
    if ($LASTEXITCODE -ne 0) {
        throw "Backend deployment failed"
    }
    
    Write-Host "✅ Backend deployed with security fixes" -ForegroundColor Green
}

# Function to deploy frontend with dynamic URLs
function Deploy-FrontendSecure {
    if ($SkipFrontend) {
        Write-Host "⏭️ Skipping frontend deployment" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🔨 Deploying frontend with dynamic URL resolution..." -ForegroundColor Cyan
    
    # Build frontend with region parameter
    Write-Host "🏗️ Building frontend..." -ForegroundColor Gray
    gcloud builds submit frontend `
        --tag gcr.io/$ProjectId/validatus-frontend:secure `
        --project=$ProjectId `
        --region=$Region `
        --timeout=600s
    
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
    
    # Get the backend URL from the deployed service dynamically
    Write-Host "🔗 Retrieving backend service URL..." -ForegroundColor Gray
    $backendUrl = gcloud run services describe validatus-backend `
        --region $Region `
        --project=$ProjectId `
        --format="value(status.url)"
    
    if ([string]::IsNullOrWhiteSpace($backendUrl)) {
        throw "Failed to retrieve backend URL"
    }
    
    Write-Host "✅ Backend URL: $backendUrl" -ForegroundColor Green
    
    # Deploy frontend with dynamic backend URL
    Write-Host "🚀 Deploying frontend to Cloud Run..." -ForegroundColor Gray
    gcloud run deploy validatus-frontend `
        --image gcr.io/$ProjectId/validatus-frontend:secure `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --memory 512Mi `
        --cpu 1 `
        --timeout 300 `
        --max-instances 5 `
        --set-env-vars "REACT_APP_API_BASE_URL=$backendUrl" `
        --project=$ProjectId
    
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend deployment failed"
    }
    
    Write-Host "✅ Frontend deployed with dynamic URL resolution" -ForegroundColor Green
}

# Function to test deployment with enhanced validation
function Test-DeploymentSecure {
    if ($SkipTests) {
        Write-Host "⏭️ Skipping deployment tests" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "🧪 Testing deployment with enhanced validation..." -ForegroundColor Cyan
    
    # Get service URLs dynamically
    Write-Host "Retrieving service URLs..." -ForegroundColor Gray
    $backendUrl = gcloud run services describe validatus-backend `
        --region $Region `
        --project=$ProjectId `
        --format="value(status.url)"
    
    $frontendUrl = gcloud run services describe validatus-frontend `
        --region $Region `
        --project=$ProjectId `
        --format="value(status.url)"
    
    if ([string]::IsNullOrWhiteSpace($backendUrl) -or [string]::IsNullOrWhiteSpace($frontendUrl)) {
        Write-Host "❌ Failed to retrieve service URLs" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Backend URL: $backendUrl" -ForegroundColor Gray
    Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Gray
    
    # Test backend health
    try {
        Write-Host "Testing backend health..." -ForegroundColor Gray
        $healthResponse = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get -TimeoutSec 30
        
        if ($healthResponse.status -eq "healthy") {
            Write-Host "✅ Backend health check passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Backend health check uncertain: $($healthResponse.status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # Test database connectivity through API
    try {
        Write-Host "Testing database connectivity..." -ForegroundColor Gray
        $topicsResponse = Invoke-RestMethod -Uri "$backendUrl/api/v3/topics" -Method Get -TimeoutSec 30
        
        if ($topicsResponse.topics -is [Array]) {
            Write-Host "✅ Database connectivity test passed (found $($topicsResponse.topics.Count) topics)" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Database connectivity uncertain - unexpected response format" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Database connectivity test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # Test frontend
    try {
        Write-Host "Testing frontend..." -ForegroundColor Gray
        $frontendResponse = Invoke-WebRequest -Uri $frontendUrl -Method Get -TimeoutSec 30
        
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Host "✅ Frontend test passed" -ForegroundColor Green
        } else {
            Write-Host "❌ Frontend test failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Frontend test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Main execution
try {
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Region: $Region" -ForegroundColor White
    Write-Host ""
    
    # Validate prerequisites
    Test-Prerequisites
    
    # Backup critical files
    Backup-CriticalFiles
    
    # Get database connection details
    $databaseUrl = Get-DatabaseURL
    
    # Deploy backend with security fixes
    Deploy-BackendSecure -DatabaseUrl $databaseUrl
    
    # Deploy frontend with dynamic URLs
    Deploy-FrontendSecure
    
    # Test the deployment
    $testPassed = Test-DeploymentSecure
    
    if ($testPassed) {
        # Get service URLs for display
        $backendUrl = gcloud run services describe validatus-backend `
            --region $Region `
            --project=$ProjectId `
            --format="value(status.url)"
        
        $frontendUrl = gcloud run services describe validatus-frontend `
            --region $Region `
            --project=$ProjectId `
            --format="value(status.url)"
        
        Write-Host ""
        Write-Host "🎉 Secure deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 Application URLs:" -ForegroundColor Cyan
        Write-Host "===================" -ForegroundColor Cyan
        Write-Host "🌐 Frontend: $frontendUrl" -ForegroundColor White
        Write-Host "🔧 Backend: $backendUrl" -ForegroundColor White
        Write-Host "📋 Health: $backendUrl/health" -ForegroundColor White
        Write-Host "📖 API Docs: $backendUrl/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "🔒 Security Features Implemented:" -ForegroundColor Cyan
        Write-Host "=================================" -ForegroundColor Cyan
        Write-Host "✅ DATABASE_URL stored in Secret Manager" -ForegroundColor Green
        Write-Host "✅ Dynamic URL resolution for multi-region support" -ForegroundColor Green
        Write-Host "✅ Critical files backed up before deployment" -ForegroundColor Green
        Write-Host "✅ Enhanced error handling and validation" -ForegroundColor Green
        Write-Host "✅ Region-aware deployment configuration" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Deployment completed but some tests failed" -ForegroundColor Yellow
        Write-Host "Please check the logs above for details" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Secure deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting tips:" -ForegroundColor Cyan
    Write-Host "- Ensure all required APIs are enabled" -ForegroundColor White
    Write-Host "- Verify Cloud SQL instance exists and is accessible" -ForegroundColor White
    Write-Host "- Check Secret Manager permissions" -ForegroundColor White
    Write-Host "- Ensure gcloud is authenticated with proper permissions" -ForegroundColor White
    exit 1
}
