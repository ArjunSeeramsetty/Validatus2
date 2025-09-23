#!/bin/bash

# Application deployment script for Validatus
# This script builds and deploys the Validatus application to Cloud Run

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
SERVICE_NAME="validatus-backend"

echo -e "${BLUE}🚀 Deploying Validatus Application${NC}"
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

# Configure Docker for GCR
echo -e "${BLUE}🐳 Configuring Docker for Google Container Registry...${NC}"
gcloud auth configure-docker

# Build the Docker image
echo -e "${BLUE}🏗️  Building Docker image...${NC}"
cd backend
docker build -f Dockerfile.gcp -t gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest .

# Push the image to GCR
echo -e "${BLUE}📤 Pushing image to Google Container Registry...${NC}"
docker push gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 1 \
    --set-env-vars GCP_PROJECT_ID=${PROJECT_ID} \
    --set-env-vars GCP_REGION=${REGION} \
    --set-env-vars VERTEX_AI_LOCATION=${REGION} \
    --set-env-vars ENABLE_GCP_MONITORING=true

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo -e "${GREEN}✅ Application deployed successfully!${NC}"
echo ""
echo -e "${BLUE}🔗 Service Information:${NC}"
echo "=========================="
echo "Service Name: ${SERVICE_NAME}"
echo "Service URL: ${SERVICE_URL}"
echo "Region: ${REGION}"
echo ""
echo -e "${BLUE}🧪 Test the deployment:${NC}"
echo "curl ${SERVICE_URL}/health"
echo ""
echo -e "${BLUE}📊 Monitor your service:${NC}"
echo "- Cloud Run Console: https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo "- Cloud Monitoring: https://console.cloud.google.com/monitoring?project=${PROJECT_ID}"
echo "- Cloud Logging: https://console.cloud.google.com/logs?project=${PROJECT_ID}"
echo ""

# Test the health endpoint
echo -e "${BLUE}🏥 Testing health endpoint...${NC}"
if curl -f -s ${SERVICE_URL}/health > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed - service may still be starting up${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Validatus Application Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Test the API endpoints"
echo "2. Set up monitoring and alerting"
echo "3. Configure custom domain (optional)"
echo "4. Set up CI/CD pipeline"
echo ""
