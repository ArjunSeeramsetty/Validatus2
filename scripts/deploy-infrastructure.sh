#!/bin/bash

# Infrastructure deployment script for Validatus
# This script deploys the complete GCP infrastructure using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="validatus-prod"
REGION="us-central1"

echo -e "${BLUE}🏗️  Deploying Validatus Infrastructure${NC}"
echo "=================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please run setup-gcp-project.sh first.${NC}"
    exit 1
fi

# Load environment variables
source .env

# Verify GCP authentication
echo -e "${BLUE}🔐 Verifying GCP authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${RED}❌ Please authenticate with Google Cloud:${NC}"
    gcloud auth login
fi

# Set the project
echo -e "${BLUE}📋 Setting project to: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# Check if required APIs are enabled
echo -e "${BLUE}🔧 Verifying required APIs are enabled...${NC}"
REQUIRED_APIS=(
    "compute.googleapis.com"
    "cloudsql.googleapis.com"
    "storage.googleapis.com"
    "aiplatform.googleapis.com"
    "cloudtasks.googleapis.com"
    "pubsub.googleapis.com"
    "run.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if ! gcloud services list --enabled --filter="name:${api}" --format="value(name)" | grep -q "${api}"; then
        echo -e "${YELLOW}⚠️  Enabling ${api}...${NC}"
        gcloud services enable ${api} --project=${PROJECT_ID}
    fi
done

echo -e "${GREEN}✅ All required APIs are enabled${NC}"

# Navigate to terraform directory
cd infrastructure/terraform

# Initialize Terraform if not already done
if [ ! -d ".terraform" ]; then
    echo -e "${BLUE}🏗️  Initializing Terraform...${NC}"
    terraform init
fi

# Plan the deployment
echo -e "${BLUE}📋 Planning infrastructure deployment...${NC}"
terraform plan -var="project_id=${PROJECT_ID}" -var="region=${REGION}"

# Ask for confirmation
echo ""
echo -e "${YELLOW}⚠️  This will create the following resources in your GCP project:${NC}"
echo "- Cloud SQL PostgreSQL instance"
echo "- Cloud Storage buckets"
echo "- Cloud Run services"
echo "- Cloud Tasks queues"
echo "- Pub/Sub topics"
echo "- IAM roles and service accounts"
echo ""
read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Apply the configuration
    echo -e "${BLUE}🚀 Deploying infrastructure...${NC}"
    terraform apply -var="project_id=${PROJECT_ID}" -var="region=${REGION}" -auto-approve
    
    echo -e "${GREEN}✅ Infrastructure deployed successfully!${NC}"
    
    # Display outputs
    echo ""
    echo -e "${BLUE}📊 Infrastructure Outputs:${NC}"
    echo "=========================="
    terraform output
    
    # Create deployment summary
    echo ""
    echo -e "${GREEN}🎉 Validatus Infrastructure Deployment Complete!${NC}"
    echo "=============================================="
    echo ""
    echo -e "${BLUE}🔗 Access your resources:${NC}"
    echo "- GCP Console: https://console.cloud.google.com/home/dashboard?project=${PROJECT_ID}"
    echo "- Cloud SQL: https://console.cloud.google.com/sql/instances?project=${PROJECT_ID}"
    echo "- Cloud Run: https://console.cloud.google.com/run?project=${PROJECT_ID}"
    echo "- Cloud Storage: https://console.cloud.google.com/storage?project=${PROJECT_ID}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "1. Update your .env file with the Cloud SQL instance details"
    echo "2. Build and deploy your application: docker-compose up --build"
    echo "3. Test the API endpoints"
    echo ""
    
else
    echo -e "${YELLOW}⏹️  Deployment cancelled.${NC}"
    exit 0
fi
