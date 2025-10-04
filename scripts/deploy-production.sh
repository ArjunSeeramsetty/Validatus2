#!/bin/bash

set -e

# Configuration
PROJECT_ID="validatus-platform"
REGION="us-central1"
SERVICE_NAME="validatus-backend"

echo "🚀 Deploying Validatus to Production..."

# Build and deploy backend
deploy_backend() {
    echo "🔨 Building and deploying backend..."
    
    # Build container image
    gcloud builds submit \
        --config=cloudbuild-production.yaml \
        --substitutions=_PROJECT_ID=$PROJECT_ID \
        --timeout=2400s \
        .
    
    echo "✅ Backend deployment completed"
}

# Test deployment
test_deployment() {
    echo "🧪 Testing deployment..."
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --region=$REGION \
        --format="value(status.url)")
    
    echo "Service URL: $SERVICE_URL"
    
    # Health check
    if curl -f "$SERVICE_URL/health" --connect-timeout 30 --max-time 60; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed"
        return 1
    fi
    
    # Test database connection
    HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health")
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        echo "✅ Service is healthy and responding"
    else
        echo "❌ Service health check indicates issues"
        echo "Response: $HEALTH_RESPONSE"
        return 1
    fi
}

# Setup monitoring
setup_monitoring() {
    echo "📊 Setting up monitoring and alerting..."
    
    # Deploy monitoring configuration
    if [ -f "scripts/deploy-monitoring.sh" ]; then
        ./scripts/deploy-monitoring.sh
    fi
    
    echo "✅ Monitoring setup completed"
}

# Main execution
main() {
    deploy_backend
    test_deployment
    setup_monitoring
    
    echo ""
    echo "🎉 Production deployment completed successfully!"
    echo ""
    echo "🌐 Service URL: $(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")"
    echo "📋 Health Check: $(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")/health"
    echo "📖 API Docs: $(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")/docs"
    echo ""
}

main "$@"