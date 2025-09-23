@echo off
REM Setup script for Validatus GCP project (Windows)
REM This script sets up the GCP project and initializes the required services

setlocal enabledelayedexpansion

REM Project configuration
set PROJECT_ID=validatus-prod
set PROJECT_NAME=Validatus
set REGION=us-central1
set ZONE=us-central1-a

echo 🚀 Setting up Validatus GCP Project
echo ==================================

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Google Cloud CLI is not installed. Please install it first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Check if user is authenticated
gcloud auth list --filter=status:ACTIVE --format="value(account)" | findstr "@" >nul
if %errorlevel% neq 0 (
    echo ⚠️  Please authenticate with Google Cloud:
    gcloud auth login
)

REM Set the project
echo 📋 Setting project to: %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Create the project if it doesn't exist
echo 🏗️  Creating GCP project...
gcloud projects describe %PROJECT_ID% >nul 2>nul
if %errorlevel% neq 0 (
    gcloud projects create %PROJECT_ID% --name="%PROJECT_NAME%" --labels=environment=prod,project=validatus
    echo ✅ Project created successfully
) else (
    echo ✅ Project already exists
)

REM Set billing account
echo 💳 Setting up billing...
echo ⚠️  Please ensure you have a billing account linked to this project
echo You can link billing at: https://console.cloud.google.com/billing/linkedaccount?project=%PROJECT_ID%

REM Enable required APIs
echo 🔧 Enabling required Google Cloud APIs...
set APIS=compute.googleapis.com cloudsql.googleapis.com storage.googleapis.com aiplatform.googleapis.com cloudtasks.googleapis.com pubsub.googleapis.com run.googleapis.com cloudbuild.googleapis.com monitoring.googleapis.com logging.googleapis.com secretmanager.googleapis.com firestore.googleapis.com servicenetworking.googleapis.com

for %%a in (%APIS%) do (
    echo   Enabling %%a...
    gcloud services enable %%a --project=%PROJECT_ID%
)

echo ✅ All APIs enabled successfully

REM Create service account for Validatus
echo 👤 Creating Validatus service account...
set SERVICE_ACCOUNT_EMAIL=validatus-service@%PROJECT_ID%.iam.gserviceaccount.com

gcloud iam service-accounts describe %SERVICE_ACCOUNT_EMAIL% >nul 2>nul
if %errorlevel% neq 0 (
    gcloud iam service-accounts create validatus-service --display-name="Validatus Service Account" --description="Service account for Validatus platform" --project=%PROJECT_ID%
    echo ✅ Service account created
) else (
    echo ✅ Service account already exists
)

REM Grant necessary roles to the service account
echo 🔐 Granting IAM roles to service account...
set ROLES=roles/storage.admin roles/cloudsql.client roles/aiplatform.user roles/cloudtasks.enqueuer roles/pubsub.publisher roles/pubsub.subscriber roles/monitoring.metricWriter roles/logging.logWriter roles/secretmanager.secretAccessor roles/firestore.serviceAgent

for %%r in (%ROLES%) do (
    echo   Granting %%r...
    gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%SERVICE_ACCOUNT_EMAIL%" --role="%%r"
)

echo ✅ IAM roles granted successfully

REM Create service account key
echo 🔑 Creating service account key...
set KEY_FILE=validatus-service-key.json
gcloud iam service-accounts keys create %KEY_FILE% --iam-account=%SERVICE_ACCOUNT_EMAIL% --project=%PROJECT_ID%

echo ✅ Service account key created: %KEY_FILE%

REM Set up environment variables
echo 📝 Creating environment configuration...
(
echo # Validatus GCP Configuration
echo GCP_PROJECT_ID=%PROJECT_ID%
echo GCP_REGION=%REGION%
echo GCP_ZONE=%ZONE%
echo.
echo # Google Cloud Credentials
echo GOOGLE_APPLICATION_CREDENTIALS=./%KEY_FILE%
echo.
echo # Storage Configuration
echo GCP_STORAGE_PREFIX=validatus
echo.
echo # AI Platform Configuration
echo VERTEX_AI_LOCATION=%REGION%
echo VERTEX_EMBEDDING_MODEL=text-embedding-004
echo.
echo # Cloud SQL Configuration
echo CLOWD_SQL_INSTANCE=validatus-db
echo CLOWD_SQL_DATABASE=validatus
echo CLOWD_SQL_USER=validatus_user
echo CLOWD_SQL_PASSWORD=CHANGE_THIS_PASSWORD
echo.
echo # Cloud Tasks Configuration
echo CLOWD_TASKS_LOCATION=%REGION%
echo SCRAPING_QUEUE_NAME=url-scraping-queue
echo.
echo # Pub/Sub Configuration
echo PUBSUB_TOPIC_PREFIX=validatus
echo.
echo # Monitoring Configuration
echo ENABLE_GCP_MONITORING=true
echo MONITORING_INTERVAL_SECONDS=60
echo.
echo # Security Configuration
echo ENABLE_VPC_NATIVE=true
echo ALLOWED_ORIGINS=["https://validatus-frontend.app", "http://localhost:3000"]
) > .env

echo ✅ Environment configuration created: .env

REM Initialize Terraform
echo 🏗️  Initializing Terraform...
cd infrastructure\terraform
terraform init

echo ✅ Terraform initialized successfully

REM Display next steps
echo.
echo 🎉 Validatus GCP Project Setup Complete!
echo ==================================
echo.
echo 📋 Next Steps:
echo 1. Update the database password in .env file
echo 2. Link a billing account to your project
echo 3. Deploy infrastructure: cd infrastructure\terraform ^&^& terraform apply
echo 4. Deploy the application: docker-compose up --build
echo.
echo 🔗 Useful Links:
echo - GCP Console: https://console.cloud.google.com/home/dashboard?project=%PROJECT_ID%
echo - Billing: https://console.cloud.google.com/billing/linkedaccount?project=%PROJECT_ID%
echo - APIs: https://console.cloud.google.com/apis/dashboard?project=%PROJECT_ID%
echo.
echo ⚠️  Important:
echo - Keep your service account key file secure: %KEY_FILE%
echo - Update the database password in .env before deploying
echo - Ensure billing is enabled before running terraform apply
echo.

pause
