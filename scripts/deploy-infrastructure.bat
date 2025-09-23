@echo off
REM Infrastructure deployment script for Validatus (Windows)
REM This script deploys the complete GCP infrastructure using Terraform

setlocal enabledelayedexpansion

REM Project configuration
set PROJECT_ID=validatus-prod
set REGION=us-central1

echo 🏗️  Deploying Validatus Infrastructure
echo ==================================

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found. Please run setup-gcp-project.bat first.
    pause
    exit /b 1
)

REM Load environment variables from .env
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
    )
)

REM Verify GCP authentication
echo 🔐 Verifying GCP authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" | findstr "@" >nul
if %errorlevel% neq 0 (
    echo ❌ Please authenticate with Google Cloud:
    gcloud auth login
)

REM Set the project
echo 📋 Setting project to: %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Check if required APIs are enabled
echo 🔧 Verifying required APIs are enabled...
set REQUIRED_APIS=compute.googleapis.com cloudsql.googleapis.com storage.googleapis.com aiplatform.googleapis.com cloudtasks.googleapis.com pubsub.googleapis.com run.googleapis.com

for %%a in (%REQUIRED_APIS%) do (
    gcloud services list --enabled --filter="name:%%a" --format="value(name)" | findstr "%%a" >nul
    if %errorlevel% neq 0 (
        echo ⚠️  Enabling %%a...
        gcloud services enable %%a --project=%PROJECT_ID%
    )
)

echo ✅ All required APIs are enabled

REM Navigate to terraform directory
cd infrastructure\terraform

REM Initialize Terraform if not already done
if not exist ".terraform" (
    echo 🏗️  Initializing Terraform...
    terraform init
)

REM Plan the deployment
echo 📋 Planning infrastructure deployment...
terraform plan -var="project_id=%PROJECT_ID%" -var="region=%REGION%"

REM Ask for confirmation
echo.
echo ⚠️  This will create the following resources in your GCP project:
echo - Cloud SQL PostgreSQL instance
echo - Cloud Storage buckets
echo - Cloud Run services
echo - Cloud Tasks queues
echo - Pub/Sub topics
echo - IAM roles and service accounts
echo.
set /p confirm="Do you want to proceed with the deployment? (y/N): "

if /i "%confirm%"=="y" (
    REM Apply the configuration
    echo 🚀 Deploying infrastructure...
    terraform apply -var="project_id=%PROJECT_ID%" -var="region=%REGION%" -auto-approve
    
    echo ✅ Infrastructure deployed successfully!
    
    REM Display outputs
    echo.
    echo 📊 Infrastructure Outputs:
    echo ==========================
    terraform output
    
    REM Create deployment summary
    echo.
    echo 🎉 Validatus Infrastructure Deployment Complete!
    echo ==============================================
    echo.
    echo 🔗 Access your resources:
    echo - GCP Console: https://console.cloud.google.com/home/dashboard?project=%PROJECT_ID%
    echo - Cloud SQL: https://console.cloud.google.com/sql/instances?project=%PROJECT_ID%
    echo - Cloud Run: https://console.cloud.google.com/run?project=%PROJECT_ID%
    echo - Cloud Storage: https://console.cloud.google.com/storage?project=%PROJECT_ID%
    echo.
    echo 📋 Next Steps:
    echo 1. Update your .env file with the Cloud SQL instance details
    echo 2. Build and deploy your application: docker-compose up --build
    echo 3. Test the API endpoints
    echo.
    
) else (
    echo ⏹️  Deployment cancelled.
)

pause
