<#
.SYNOPSIS
    Set up GCP Infrastructure for Validatus using Terraform
.DESCRIPTION
    This script sets up all required GCP resources for Validatus platform
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    [string]$Zone = "us-central1-a",
    [switch]$SkipPlan,
    [switch]$AutoApprove
)

Write-Host "🚀 Setting up GCP Infrastructure for Validatus..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Configuration
$TerraformDir = "infrastructure\terraform"
$ErrorActionPreference = "Stop"

# Function to check dependencies
function Test-Dependencies {
    Write-Host "🔍 Checking dependencies..." -ForegroundColor Cyan
    
    $missing = @()
    
    if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
        $missing += "gcloud CLI"
    }
    
    if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
        $missing += "Terraform"
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "❌ Missing dependencies: $($missing -join ', ')" -ForegroundColor Red
        Write-Host "Please run Install-Prerequisites.ps1 first" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Dependencies check passed" -ForegroundColor Green
}

# Function to setup Google Cloud authentication
function Initialize-GCloudAuth {
    Write-Host "🔐 Setting up Google Cloud authentication..." -ForegroundColor Cyan
    
    # Check if already authenticated
    $activeAccount = gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>$null
    
    if (-not $activeAccount) {
        Write-Host "Please authenticate with Google Cloud:" -ForegroundColor Yellow
        gcloud auth login
    }
    
    # Set the project
    gcloud config set project $ProjectId
    
    # Enable Application Default Credentials
    Write-Host "Setting up Application Default Credentials..." -ForegroundColor Cyan
    gcloud auth application-default login
    
    Write-Host "✅ Google Cloud authentication setup complete" -ForegroundColor Green
}

# Function to initialize Terraform
function Initialize-Terraform {
    Write-Host "🏗️ Initializing Terraform..." -ForegroundColor Cyan
    
    if (-not (Test-Path $TerraformDir)) {
        Write-Host "❌ Terraform directory not found: $TerraformDir" -ForegroundColor Red
        exit 1
    }
    
    Set-Location $TerraformDir
    
    # Initialize Terraform
    terraform init
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform initialization failed" -ForegroundColor Red
        exit 1
    }
    
    # Validate configuration
    terraform validate
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform validation failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Terraform initialized successfully" -ForegroundColor Green
}

# Function to plan and apply infrastructure
function Deploy-Infrastructure {
    Write-Host "📋 Planning infrastructure deployment..." -ForegroundColor Cyan
    
    $planArgs = @(
        "plan",
        "-var=project_id=$ProjectId",
        "-var=region=$Region",
        "-var=zone=$Zone",
        "-out=tfplan"
    )
    
    if (-not $SkipPlan) {
        # Generate Terraform plan
        & terraform @planArgs
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Terraform planning failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "📊 Terraform plan generated. Review the plan above." -ForegroundColor Cyan
        Write-Host ""
        
        if (-not $AutoApprove) {
            $response = Read-Host "Do you want to proceed with infrastructure deployment? (y/N)"
            if ($response -notmatch "^[Yy]$") {
                Write-Host "⏸️ Infrastructure deployment cancelled." -ForegroundColor Yellow
                Remove-Item "tfplan" -ErrorAction SilentlyContinue
                exit 0
            }
        }
    }
    
    Write-Host "🚀 Applying Terraform plan..." -ForegroundColor Cyan
    terraform apply tfplan
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform apply failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Infrastructure deployment completed successfully!" -ForegroundColor Green
    
    # Clean up plan file
    Remove-Item "tfplan" -ErrorAction SilentlyContinue
}

# Function to generate environment configuration
function New-EnvironmentConfig {
    Write-Host "📝 Generating environment configuration..." -ForegroundColor Cyan
    
    # Extract Terraform outputs
    terraform output -json | Out-File -FilePath "outputs.json" -Encoding utf8
    
    # Read outputs
    $outputs = Get-Content "outputs.json" | ConvertFrom-Json
    
    # Generate .env file
    $envContent = @"
# Generated GCP Environment Configuration
# Generated on: $(Get-Date)

# GCP Project Configuration
GCP_PROJECT_ID=$ProjectId
GCP_REGION=$Region
GCP_ZONE=$Zone
ENVIRONMENT=production

# Cloud SQL Configuration
CLOUD_SQL_CONNECTION_NAME=$($outputs.cloud_sql_connection_name.value)
CLOUD_SQL_DATABASE=$($outputs.database_name.value)
CLOUD_SQL_USER=$($outputs.database_user.value)
CLOUD_SQL_PASSWORD_SECRET=cloud-sql-password

# Cloud Storage Configuration
CONTENT_STORAGE_BUCKET=$($outputs.content_bucket_name.value)
EMBEDDINGS_STORAGE_BUCKET=$($outputs.embeddings_bucket_name.value)
REPORTS_STORAGE_BUCKET=$($outputs.reports_bucket_name.value)

# Vertex AI Configuration
VECTOR_SEARCH_LOCATION=$Region
EMBEDDING_MODEL=text-embedding-004
VECTOR_DIMENSIONS=768

# Memorystore Redis Configuration
REDIS_HOST=$($outputs.redis_host.value)
REDIS_PORT=$($outputs.redis_port.value)

# Cloud Spanner Configuration
SPANNER_INSTANCE_ID=$($outputs.spanner_instance_id.value)
SPANNER_DATABASE_ID=$($outputs.spanner_database_id.value)

# Service Account Configuration
SERVICE_ACCOUNT_EMAIL=$($outputs.service_account_email.value)

# Application Configuration
LOCAL_DEVELOPMENT_MODE=false
USE_IAM_AUTH=true
MAX_CONCURRENT_OPERATIONS=50
CONNECTION_POOL_SIZE=20
QUERY_TIMEOUT_SECONDS=30

# Performance Configuration
ENABLE_CACHING=true
CACHE_TTL=3600

# Monitoring Configuration
ENABLE_MONITORING=true
LOG_LEVEL=INFO
"@

    $envPath = "..\..\..\.env.production"
    $envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline
    
    Write-Host "✅ Environment configuration generated: .env.production" -ForegroundColor Green
    
    # Clean up
    Remove-Item "outputs.json" -ErrorAction SilentlyContinue
    
    # Return to original directory
    Set-Location ..\..
}

# Function to setup database schema
function Initialize-DatabaseSchema {
    Write-Host "🗄️ Setting up database schema..." -ForegroundColor Cyan
    
    Set-Location "backend"
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
        python -m venv venv
    }
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Install dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    pip install -r requirements-gcp.txt
    
    # Load environment variables and run database setup
    Write-Host "Setting up database schema..." -ForegroundColor Cyan
    
    # Load environment variables safely
    $envFile = Get-Content "..\.env.production"
    foreach ($line in $envFile) {
        # Skip comments and empty lines
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $equalsIndex = $line.IndexOf("=")
            if ($equalsIndex -gt 0) {
                $key = $line.Substring(0, $equalsIndex).Trim()
                $value = $line.Substring($equalsIndex + 1).Trim()
                
                # Handle quoted values
                if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                    $value = $value.Substring(1, $value.Length - 2)
                } elseif ($value.StartsWith("'") -and $value.EndsWith("'")) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
                
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    
    python -c @"
import asyncio
from app.services.gcp_persistence_manager import get_gcp_persistence_manager

async def setup_db():
    manager = get_gcp_persistence_manager()
    await manager.initialize()
    print('✅ Database schema setup completed')
    await manager.close()

asyncio.run(setup_db())
"@
    
    # Deactivate virtual environment
    deactivate
    
    Set-Location "..\infrastructure\terraform"
    Write-Host "✅ Database schema setup completed" -ForegroundColor Green
}

# Function to verify deployment
function Test-Deployment {
    Write-Host "🧪 Verifying deployment..." -ForegroundColor Cyan
    
    try {
        # Test Cloud SQL connection
        Write-Host "Testing Cloud SQL connection..." -ForegroundColor Cyan
        $sqlTest = gcloud sql connect validatus-primary --user=validatus_app --quiet 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Cloud SQL connection successful" -ForegroundColor Green
        } else {
            Write-Host "❌ Cloud SQL connection failed" -ForegroundColor Red
        }
        
        # Test storage buckets
        Write-Host "Testing Cloud Storage buckets..." -ForegroundColor Cyan
        $contentBucket = terraform output -raw content_bucket_name
        $storageTest = gsutil ls "gs://$contentBucket" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Cloud Storage buckets accessible" -ForegroundColor Green
        } else {
            Write-Host "❌ Cloud Storage buckets not accessible" -ForegroundColor Red
        }
        
        # Test Redis connection
        Write-Host "Testing Redis connection..." -ForegroundColor Cyan
        $redisHost = terraform output -raw redis_host
        $redisPort = terraform output -raw redis_port
        
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.ConnectAsync($redisHost, $redisPort).Wait(5000)
            if ($tcpClient.Connected) {
                Write-Host "✅ Redis connection successful" -ForegroundColor Green
                $tcpClient.Close()
            } else {
                Write-Host "❌ Redis connection failed" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Redis connection failed: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "❌ Deployment verification failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "✅ Deployment verification completed" -ForegroundColor Green
}

# Main execution
try {
    Write-Host "🎯 Validatus GCP Infrastructure Setup" -ForegroundColor Cyan
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Region: $Region" -ForegroundColor White
    Write-Host "=====================================" -ForegroundColor Cyan
    
    Test-Dependencies
    Initialize-GCloudAuth
    Initialize-Terraform
    Deploy-Infrastructure
    New-EnvironmentConfig
    Initialize-DatabaseSchema
    Test-Deployment
    
    Write-Host ""
    Write-Host "🎉 GCP Infrastructure setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Review the generated .env.production file" -ForegroundColor White
    Write-Host "2. Deploy your application using: .\Deploy-Production.ps1" -ForegroundColor White
    Write-Host "3. Configure your domain and SSL certificates" -ForegroundColor White
    Write-Host "4. Set up monitoring and alerting" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Your Validatus infrastructure is ready for production!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Infrastructure setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}
