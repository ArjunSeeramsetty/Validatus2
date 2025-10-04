#!/bin/bash
set -euo pipefail

PROJECT_ID="validatus-platform"
REGION="us-central1"
SERVICE_NAME="validatus-backend"

echo "🚀 Starting production deployment..."

# Check if base image exists, build if not
echo "📦 Checking base image..."
if ! gcloud container images describe gcr.io/$PROJECT_ID/validatus-base:latest --quiet 2>/dev/null; then
    echo "Building base image..."
    gcloud builds submit \
        --config=cloudbuild-base.yaml \
        --timeout=1200s \
        backend/
fi

# Build and deploy with production config
echo "🔨 Building and deploying application..."
gcloud builds submit \
    --config=cloudbuild-production.yaml \
    --timeout=2400s \
    .

# Test deployment
echo "🧪 Testing deployment..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

echo "Service URL: $SERVICE_URL"

# Health check
if curl -f "$SERVICE_URL/health" --connect-timeout 10 --max-time 30; then
    echo "✅ Deployment successful! Service is healthy."
    echo "🌐 Backend URL: $SERVICE_URL"
    echo "📋 Health Check: $SERVICE_URL/health"
    echo "📖 API Docs: $SERVICE_URL/docs"
else
    echo "❌ Health check failed"
    exit 1
fi
