# Validatus Production Setup - PowerShell Script for Windows
# This script sets up the complete GCP infrastructure and deploys the application

param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1"
)

Write-Host "🚀 Validatus Production Setup - PowerShell Deployment" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend/app/main_gcp.py")) {
    Write-Host "❌ Please run this script from the Validatus2 project root directory" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow

# Check gcloud
try {
    $gcloudVersion = gcloud version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud not found"
    }
    Write-Host "✅ Google Cloud SDK found" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud SDK not found. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check terraform
try {
    $terraformVersion = terraform version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "terraform not found"
    }
    Write-Host "✅ Terraform found" -ForegroundColor Green
} catch {
    Write-Host "❌ Terraform not found. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://www.terraform.io/downloads" -ForegroundColor Yellow
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "python not found"
    }
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Set up authentication
Write-Host "🔐 Setting up Google Cloud authentication..." -ForegroundColor Yellow

# Check if already authenticated
$currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if ([string]::IsNullOrEmpty($currentAccount)) {
    Write-Host "Please authenticate with Google Cloud..." -ForegroundColor Yellow
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Authentication failed" -ForegroundColor Red
        exit 1
    }
}

# Set the project
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project" -ForegroundColor Red
    exit 1
}

# Enable Application Default Credentials
gcloud auth application-default login
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set up application default credentials" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Authentication setup complete" -ForegroundColor Green

# Step 1: Set up infrastructure
Write-Host "📋 Step 1: Setting up GCP infrastructure..." -ForegroundColor Cyan

Push-Location "infrastructure/terraform"

# Initialize Terraform
terraform init
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform initialization failed" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Plan infrastructure
terraform plan -var="project_id=$ProjectId" -var="region=$Region"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform plan failed" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Ask for confirmation
$confirm = Read-Host "Do you want to proceed with infrastructure deployment? (y/N)"
if ($confirm -notmatch "^[Yy]$") {
    Write-Host "⏸️ Infrastructure deployment cancelled." -ForegroundColor Yellow
    Pop-Location
    exit 0
}

# Apply infrastructure
terraform apply -var="project_id=$ProjectId" -var="region=$Region" -auto-approve
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Infrastructure deployment failed" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "✅ Infrastructure deployment completed" -ForegroundColor Green
Pop-Location

# Step 2: Generate environment configuration
Write-Host "📋 Step 2: Generating environment configuration..." -ForegroundColor Cyan

Push-Location "infrastructure/terraform"

# Generate .env file from Terraform outputs
$envContent = @"
# Generated GCP Environment Configuration
# Generated on: $(Get-Date)

# GCP Project Configuration
GCP_PROJECT_ID=$ProjectId
GCP_REGION=$Region
GCP_ZONE=${Region}-a
ENVIRONMENT=production

# Cloud SQL Configuration
CLOUD_SQL_CONNECTION_NAME=$(terraform output -raw cloud_sql_connection_name)
CLOUD_SQL_DATABASE=$(terraform output -raw database_name)
CLOUD_SQL_USER=$(terraform output -raw database_user)
CLOUD_SQL_PASSWORD_SECRET=cloud-sql-password

# Cloud Storage Configuration
CONTENT_STORAGE_BUCKET=$(terraform output -raw content_bucket_name)
EMBEDDINGS_STORAGE_BUCKET=$(terraform output -raw embeddings_bucket_name)
REPORTS_STORAGE_BUCKET=$(terraform output -raw reports_bucket_name)

# Vertex AI Configuration
VECTOR_SEARCH_LOCATION=$Region
EMBEDDING_MODEL=text-embedding-004
VECTOR_DIMENSIONS=768

# Memorystore Redis Configuration
REDIS_HOST=$(terraform output -raw redis_host)
REDIS_PORT=$(terraform output -raw redis_port)

# Cloud Spanner Configuration
SPANNER_INSTANCE_ID=$(terraform output -raw spanner_instance_id)
SPANNER_DATABASE_ID=$(terraform output -raw spanner_database_id)

# Service Account Configuration
SERVICE_ACCOUNT_EMAIL=$(terraform output -raw service_account_email)

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

$envContent | Out-File -FilePath "../../backend/.env.production" -Encoding UTF8
Write-Host "✅ Environment configuration generated" -ForegroundColor Green

Pop-Location

# Step 3: Set up database
Write-Host "📋 Step 3: Setting up database schema..." -ForegroundColor Cyan

Push-Location "backend"

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment and install dependencies
& "venv/Scripts/Activate.ps1"
pip install -r requirements-gcp.txt

# Set environment variables and run database setup
Get-Content ".env.production" | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

python scripts/setup_database.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Database setup failed" -ForegroundColor Red
    deactivate
    Pop-Location
    exit 1
}

deactivate
Write-Host "✅ Database setup completed" -ForegroundColor Green
Pop-Location

# Step 4: Deploy application
Write-Host "📋 Step 4: Deploying application..." -ForegroundColor Cyan

gcloud builds submit --config=cloudbuild-production.yaml --timeout=2400s .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Application deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Application deployment completed" -ForegroundColor Green

# Step 5: Verify deployment
Write-Host "📋 Step 5: Verifying deployment..." -ForegroundColor Cyan

# Get service URL
$serviceUrl = gcloud run services describe validatus-backend --region=$Region --format="value(status.url)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to get service URL" -ForegroundColor Red
    exit 1
}

Write-Host "Service URL: $serviceUrl" -ForegroundColor Green

# Test health check
try {
    $response = Invoke-WebRequest -Uri "$serviceUrl/health" -UseBasicParsing -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Health check passed" -ForegroundColor Green
        $healthData = $response.Content | ConvertFrom-Json
        Write-Host "Service Status: $($healthData.status)" -ForegroundColor Green
    } else {
        Write-Host "❌ Health check failed: Status $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Validatus production setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Quick Links:" -ForegroundColor Cyan
Write-Host "• Application: $serviceUrl" -ForegroundColor White
Write-Host "• Health Check: $serviceUrl/health" -ForegroundColor White
Write-Host "• API Docs: $serviceUrl/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure your frontend to use the new backend URL" -ForegroundColor White
Write-Host "2. Set up custom domain and SSL certificates" -ForegroundColor White
Write-Host "3. Configure monitoring and alerting" -ForegroundColor White
Write-Host "4. Set up backup and disaster recovery procedures" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Your Validatus platform is ready for production use!" -ForegroundColor Green
