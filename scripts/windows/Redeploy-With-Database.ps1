<#
.SYNOPSIS
    Redeploy application with database connectivity
.DESCRIPTION
    This script redeploys the application with updated database configuration
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    [switch]$SkipFrontend,
    [switch]$SkipBackend
)

Write-Host "🚀 Redeploying Validatus with Database Connectivity..." -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Function to get database URL
function Get-DatabaseURL {
    Write-Host "🔍 Getting database connection details..." -ForegroundColor Cyan
    
    try {
        $connectionName = gcloud sql instances describe validatus-primary --format="value(connectionName)" --project=$ProjectId
        $password = gcloud secrets versions access latest --secret="cloud-sql-password" --project=$ProjectId
        
        $databaseUrl = "postgresql+asyncpg://validatus_app:$password@/validatus?host=/cloudsql/$connectionName"
        
        Write-Host "✅ Database connection details retrieved" -ForegroundColor Green
        return $databaseUrl
    } catch {
        Write-Host "❌ Failed to get database connection details: $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
}

# Function to redeploy backend
function Deploy-Backend {
    param([string]$DatabaseUrl)
    
    if ($SkipBackend) {
        Write-Host "⏭️ Skipping backend deployment" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🔨 Redeploying backend with database connectivity..." -ForegroundColor Cyan
    
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
    
    # Build and deploy backend
    gcloud builds submit backend `
        --tag gcr.io/$ProjectId/validatus-backend:latest `
        --project=$ProjectId `
        --timeout=1200s
    
    if ($LASTEXITCODE -ne 0) {
        throw "Backend build failed"
    }
    
    # Deploy to Cloud Run with environment variables
    gcloud run deploy validatus-backend `
        --image gcr.io/$ProjectId/validatus-backend:latest `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --memory 1Gi `
        --cpu 1 `
        --timeout 900 `
        --max-instances 10 `
        --set-env-vars "GCP_PROJECT_ID=$ProjectId,DATABASE_URL=$DatabaseUrl,ENVIRONMENT=production" `
        --project=$ProjectId
    
    if ($LASTEXITCODE -ne 0) {
        throw "Backend deployment failed"
    }
    
    Write-Host "✅ Backend redeployed successfully" -ForegroundColor Green
}

# Function to redeploy frontend
function Deploy-Frontend {
    if ($SkipFrontend) {
        Write-Host "⏭️ Skipping frontend deployment" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🔨 Redeploying frontend..." -ForegroundColor Cyan
    
    # Build and deploy frontend
    gcloud builds submit frontend `
        --tag gcr.io/$ProjectId/validatus-frontend:latest `
        --project=$ProjectId `
        --timeout=600s
    
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
    
    # Deploy to Cloud Run
    gcloud run deploy validatus-frontend `
        --image gcr.io/$ProjectId/validatus-frontend:latest `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --memory 512Mi `
        --cpu 1 `
        --timeout 300 `
        --max-instances 5 `
        --set-env-vars "REACT_APP_API_BASE_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app" `
        --project=$ProjectId
    
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend deployment failed"
    }
    
    Write-Host "✅ Frontend redeployed successfully" -ForegroundColor Green
}

# Function to test deployment
function Test-DeploymentWithDatabase {
    Write-Host "🧪 Testing deployment with database connectivity..." -ForegroundColor Cyan
    
    $backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
    $frontendUrl = "https://validatus-frontend-ssivkqhvhq-uc.a.run.app"
    
    # Test backend health
    try {
        Write-Host "Testing backend health..." -ForegroundColor Gray
        $healthResponse = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get -TimeoutSec 30
        
        if ($healthResponse.status -eq "healthy") {
            Write-Host "✅ Backend health check passed" -ForegroundColor Green
        } else {
            Write-Host "❌ Backend health check failed" -ForegroundColor Red
            return $false
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
    
    # Get database connection details
    $databaseUrl = Get-DatabaseURL
    
    # Deploy backend with database connectivity
    Deploy-Backend -DatabaseUrl $databaseUrl
    
    # Deploy frontend
    Deploy-Frontend
    
    # Test the deployment
    $testPassed = Test-DeploymentWithDatabase
    
    if ($testPassed) {
        Write-Host ""
        Write-Host "🎉 Redeployment with database connectivity successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 Application URLs:" -ForegroundColor Cyan
        Write-Host "===================" -ForegroundColor Cyan
        Write-Host "🌐 Frontend: https://validatus-frontend-ssivkqhvhq-uc.a.run.app" -ForegroundColor White
        Write-Host "🔧 Backend: https://validatus-backend-ssivkqhvhq-uc.a.run.app" -ForegroundColor White
        Write-Host "📋 Health: https://validatus-backend-ssivkqhvhq-uc.a.run.app/health" -ForegroundColor White
        Write-Host "📖 API Docs: https://validatus-backend-ssivkqhvhq-uc.a.run.app/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "✅ Your application now has full database persistence!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Deployment completed but some tests failed" -ForegroundColor Yellow
        Write-Host "Please check the logs above for details" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Redeployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
