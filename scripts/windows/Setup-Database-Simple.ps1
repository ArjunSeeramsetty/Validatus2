<#
.SYNOPSIS
    Simple database setup for Validatus
.DESCRIPTION
    This script creates a minimal database setup for Validatus
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$Region = "us-central1"
)

Write-Host "🗄️ Setting up Validatus Database (Simple)" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

try {
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Region: $Region" -ForegroundColor White
    Write-Host ""
    
    # Step 1: Enable required APIs
    Write-Host "📋 Step 1: Enabling required APIs..." -ForegroundColor Cyan
    $apis = @("sqladmin.googleapis.com", "redis.googleapis.com", "secretmanager.googleapis.com")
    foreach ($api in $apis) {
        Write-Host "Enabling $api..." -ForegroundColor Gray
        gcloud services enable $api --project=$ProjectId
    }
    Write-Host "✅ APIs enabled" -ForegroundColor Green
    Write-Host ""
    
    # Step 2: Check if database instance exists
    Write-Host "📋 Step 2: Checking database instance..." -ForegroundColor Cyan
    gcloud sql instances describe validatus-primary --project=$ProjectId 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cloud SQL instance already exists" -ForegroundColor Green
        
        # Get password from Secret Manager
        try {
            $password = gcloud secrets versions access latest --secret="cloud-sql-password" --project=$ProjectId
            Write-Host "✅ Retrieved existing database password" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to retrieve password from Secret Manager" -ForegroundColor Red
            throw "Please ensure the cloud-sql-password secret exists"
        }
    } else {
        Write-Host "❌ Cloud SQL instance does not exist" -ForegroundColor Red
        Write-Host "Please create the database instance first using the full infrastructure setup" -ForegroundColor Yellow
        throw "Database instance not found"
    }
    
    # Step 3: Test database connection
    Write-Host "📋 Step 3: Testing database connection..." -ForegroundColor Cyan
    try {
        $env:PGPASSWORD = $password
        gcloud sql connect validatus-primary --user=validatus_app --database=validatus --quiet --command="SELECT COUNT(*) FROM topics;" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database connection test successful" -ForegroundColor Green
        } else {
            Write-Host "❌ Database connection test failed" -ForegroundColor Red
            Write-Host "This might be expected if the schema hasn't been created yet" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Database connection test failed: $($_.Exception.Message)" -ForegroundColor Yellow
    } finally {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
    
    # Step 4: Create environment configuration
    Write-Host "📋 Step 4: Creating environment configuration..." -ForegroundColor Cyan
    
    # Get connection name
    $connectionName = gcloud sql instances describe validatus-primary --format="value(connectionName)" --project=$ProjectId
    
    # Create environment configuration
    $envContent = "# Validatus Production Environment Configuration`n"
    $envContent += "# Generated on: $(Get-Date)`n`n"
    $envContent += "GCP_PROJECT_ID=$ProjectId`n"
    $envContent += "GCP_REGION=$Region`n"
    $envContent += "ENVIRONMENT=production`n"
    # Dynamically construct URLs or leave as template
    $envContent += "FRONTEND_URL=https://validatus-frontend-${ProjectId}.run.app`n"
    $envContent += "BACKEND_URL=https://validatus-backend-${ProjectId}.run.app`n"
    # Reference secret instead of embedding password
    $envContent += "DATABASE_URL=postgresql+asyncpg://validatus_app:[SECRET]@/validatus?host=/cloudsql/$connectionName`n"
    $envContent += "CLOUD_SQL_PASSWORD_SECRET=cloud-sql-password`n"
    $envContent += "CLOUD_SQL_CONNECTION_NAME=$connectionName`n"
    $envContent += "CLOUD_SQL_DATABASE=validatus`n"
    $envContent += "CLOUD_SQL_USER=validatus_app`n"
    $envContent += "LOCAL_DEVELOPMENT_MODE=false`n"
    $envContent += "ENABLE_CACHING=true`n"
    $envContent += "LOG_LEVEL=INFO`n"

    $envPath = ".env.production"
    $envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline
    
    Write-Host "✅ Environment configuration saved to .env.production" -ForegroundColor Green
    
    # Add .env.production to .gitignore to prevent accidental commits
    $gitignorePath = ".gitignore"
    if (Test-Path $gitignorePath) {
        $gitignoreContent = Get-Content $gitignorePath -Raw
        if ($gitignoreContent -notmatch "\.env\.production") {
            Add-Content $gitignorePath "`n.env.production"
            Write-Host "✅ Added .env.production to .gitignore" -ForegroundColor Green
        }
    } else {
        ".env.production" | Out-File -FilePath $gitignorePath -Encoding utf8
        Write-Host "✅ Created .gitignore with .env.production" -ForegroundColor Green
    }
    
    # Success summary
    Write-Host ""
    Write-Host "🎉 Database setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Setup Summary:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    Write-Host "✅ Cloud SQL instance: validatus-primary" -ForegroundColor White
    Write-Host "✅ Database: validatus" -ForegroundColor White
    Write-Host "✅ User: validatus_app" -ForegroundColor White
    Write-Host "✅ Environment: .env.production updated" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Test the database connection" -ForegroundColor White
    Write-Host "2. Update your application configuration" -ForegroundColor White
    Write-Host "3. Redeploy your backend with database connectivity" -ForegroundColor White
    
} catch {
    Write-Host "❌ Database setup failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
