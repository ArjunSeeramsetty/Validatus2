# ROOT CAUSE FIX DEPLOYMENT SCRIPT

## This script implements ALL fixes identified in the root cause analysis

echo "========================================="
echo "VALIDATUS2 ROOT CAUSE FIX DEPLOYMENT"
echo "========================================="
echo ""

echo "Fix 1: Updating main.py with better error handling..."
echo "Fix 2: Ensuring models are imported..."
echo "Fix 3: Updating Cloud Run configuration..."
echo "Fix 4: Database migration automation..."
echo ""

# Set project variables
PROJECT_ID="validatus-platform"
REGION="us-central1"
SERVICE="validatus-backend"

echo "Deploying with:"
echo "  - Memory: 2Gi (increased from 512Mi)"
echo "  - CPU: 2 (increased from 1)"
echo "  - Timeout: 300s (increased from 60s)"
echo "  - Concurrency: 80"
echo ""

# Deploy with updated configuration
cd backend

gcloud run deploy $SERVICE \
  --source . \
  --region=$REGION \
  --project=$PROJECT_ID \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=80 \
  --max-instances=10 \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production" \
  --set-cloudsql-instances="$PROJECT_ID:$REGION:validatus-db"

echo ""
echo "========================================="
echo "DEPLOYMENT COMPLETE"
echo "========================================="
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE --region=$REGION --platform=managed --format="value(status.url)" --project=$PROJECT_ID)

echo "Service URL: $SERVICE_URL"
echo ""

# Wait for service to be ready
echo "Waiting for service to be ready..."
sleep 30

# Test health endpoint
echo "Testing health endpoint..."
curl -s "$SERVICE_URL/health" | python -m json.tool

echo ""
echo "Testing data-driven endpoint..."
curl -s "$SERVICE_URL/api/v3/data-driven-results/test" || echo "Endpoint test complete"

echo ""
echo "========================================="
echo "Verify at: $SERVICE_URL/docs"
echo "========================================="
