#!/bin/bash

# Setup script for Validatus GCP project
# This script sets up the GCP project and initializes the required services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="validatus-prod"
PROJECT_NAME="Validatus"
REGION="us-central1"
ZONE="us-central1-a"

echo -e "${BLUE}🚀 Setting up Validatus GCP Project${NC}"
echo "=================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${YELLOW}⚠️  Please authenticate with Google Cloud:${NC}"
    gcloud auth login
fi

# Set the project
echo -e "${BLUE}📋 Setting project to: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# Create the project if it doesn't exist
echo -e "${BLUE}🏗️  Creating GCP project...${NC}"
if ! gcloud projects describe ${PROJECT_ID} &> /dev/null; then
    gcloud projects create ${PROJECT_ID} --name="${PROJECT_NAME}" --labels=environment=prod,project=validatus
    echo -e "${GREEN}✅ Project created successfully${NC}"
else
    echo -e "${GREEN}✅ Project already exists${NC}"
fi

# Set billing account (you'll need to replace with your billing account ID)
echo -e "${BLUE}💳 Setting up billing...${NC}"
echo -e "${YELLOW}⚠️  Please ensure you have a billing account linked to this project${NC}"
echo "You can link billing at: https://console.cloud.google.com/billing/linkedaccount?project=${PROJECT_ID}"

# Enable required APIs
echo -e "${BLUE}🔧 Enabling required Google Cloud APIs...${NC}"
APIS=(
    "compute.googleapis.com"
    "cloudsql.googleapis.com"
    "storage.googleapis.com"
    "aiplatform.googleapis.com"
    "cloudtasks.googleapis.com"
    "pubsub.googleapis.com"
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "monitoring.googleapis.com"
    "logging.googleapis.com"
    "secretmanager.googleapis.com"
    "firestore.googleapis.com"
    "servicenetworking.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo -e "${BLUE}  Enabling ${api}...${NC}"
    gcloud services enable ${api} --project=${PROJECT_ID}
done

echo -e "${GREEN}✅ All APIs enabled successfully${NC}"

# Create service account for Validatus
echo -e "${BLUE}👤 Creating Validatus service account...${NC}"
SERVICE_ACCOUNT_EMAIL="validatus-service@${PROJECT_ID}.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} &> /dev/null; then
    gcloud iam service-accounts create validatus-service \
        --display-name="Validatus Service Account" \
        --description="Service account for Validatus platform" \
        --project=${PROJECT_ID}
    echo -e "${GREEN}✅ Service account created${NC}"
else
    echo -e "${GREEN}✅ Service account already exists${NC}"
fi

# Grant necessary roles to the service account
echo -e "${BLUE}🔐 Granting IAM roles to service account...${NC}"
ROLES=(
    "roles/storage.admin"
    "roles/cloudsql.client"
    "roles/aiplatform.user"
    "roles/cloudtasks.enqueuer"
    "roles/pubsub.publisher"
    "roles/pubsub.subscriber"
    "roles/monitoring.metricWriter"
    "roles/logging.logWriter"
    "roles/secretmanager.secretAccessor"
    "roles/firestore.serviceAgent"
)

for role in "${ROLES[@]}"; do
    echo -e "${BLUE}  Granting ${role}...${NC}"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="${role}"
done

echo -e "${GREEN}✅ IAM roles granted successfully${NC}"

# Create service account key
echo -e "${BLUE}🔑 Creating service account key...${NC}"
KEY_FILE="validatus-service-key.json"
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

echo -e "${GREEN}✅ Service account key created: ${KEY_FILE}${NC}"

# Set up environment variables
echo -e "${BLUE}📝 Creating environment configuration...${NC}"
cat > .env << EOF
# Validatus GCP Configuration
GCP_PROJECT_ID=${PROJECT_ID}
GCP_REGION=${REGION}
GCP_ZONE=${ZONE}

# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS=./${KEY_FILE}

# Storage Configuration
GCP_STORAGE_PREFIX=validatus

# AI Platform Configuration
VERTEX_AI_LOCATION=${REGION}
VERTEX_EMBEDDING_MODEL=text-embedding-004

# Cloud SQL Configuration
CLOUD_SQL_INSTANCE=validatus-db
CLOUD_SQL_DATABASE=validatus
CLOUD_SQL_USER=validatus_user
CLOUD_SQL_PASSWORD=CHANGE_THIS_PASSWORD

# Cloud Tasks Configuration
CLOUD_TASKS_LOCATION=${REGION}
SCRAPING_QUEUE_NAME=url-scraping-queue

# Pub/Sub Configuration
PUBSUB_TOPIC_PREFIX=validatus

# Monitoring Configuration
ENABLE_GCP_MONITORING=true
MONITORING_INTERVAL_SECONDS=60

# Security Configuration
ENABLE_VPC_NATIVE=true
ALLOWED_ORIGINS=["https://validatus-frontend.app", "http://localhost:3000"]
EOF

echo -e "${GREEN}✅ Environment configuration created: .env${NC}"

# Initialize Terraform
echo -e "${BLUE}🏗️  Initializing Terraform...${NC}"
cd infrastructure/terraform
terraform init

echo -e "${GREEN}✅ Terraform initialized successfully${NC}"

# Display next steps
echo ""
echo -e "${GREEN}🎉 Validatus GCP Project Setup Complete!${NC}"
echo "=================================="
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Update the database password in .env file"
echo "2. Link a billing account to your project"
echo "3. Deploy infrastructure: cd infrastructure/terraform && terraform apply"
echo "4. Deploy the application: docker-compose up --build"
echo ""
echo -e "${BLUE}🔗 Useful Links:${NC}"
echo "- GCP Console: https://console.cloud.google.com/home/dashboard?project=${PROJECT_ID}"
echo "- Billing: https://console.cloud.google.com/billing/linkedaccount?project=${PROJECT_ID}"
echo "- APIs: https://console.cloud.google.com/apis/dashboard?project=${PROJECT_ID}"
echo ""
echo -e "${RED}⚠️  Important:${NC}"
echo "- Keep your service account key file secure: ${KEY_FILE}"
echo "- Update the database password in .env before deploying"
echo "- Ensure billing is enabled before running terraform apply"
echo ""
