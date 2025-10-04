#!/bin/bash
# setup-validatus-production.sh

set -e

PROJECT_ID="validatus-platform"
REGION="us-central1"

echo "🚀 Validatus Production Setup - One Command Deploy"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "backend/app/main_gcp.py" ]; then
    echo "❌ Please run this script from the Validatus2 project root directory"
    exit 1
fi

# Step 1: Set up infrastructure
echo "📋 Step 1: Setting up GCP infrastructure..."
if [ -f "scripts/setup-gcp-infrastructure.sh" ]; then
    chmod +x scripts/setup-gcp-infrastructure.sh
    ./scripts/setup-gcp-infrastructure.sh
else
    echo "❌ Infrastructure setup script not found"
    exit 1
fi

# Step 2: Set up database
echo "📋 Step 2: Setting up database schema..."
cd backend
if [ -f "scripts/setup_database.py" ]; then
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements-gcp.txt
    python scripts/setup_database.py
    deactivate
else
    echo "❌ Database setup script not found"
    exit 1
fi
cd ..

# Step 3: Deploy application
echo "📋 Step 3: Deploying application..."
if [ -f "scripts/deploy-production.sh" ]; then
    chmod +x scripts/deploy-production.sh
    ./scripts/deploy-production.sh
else
    echo "❌ Deployment script not found"
    exit 1
fi

# Step 4: Verify deployment
echo "📋 Step 4: Verifying deployment..."
if [ -f "scripts/verify-production.py" ]; then
    python scripts/verify-production.py
else
    echo "⚠️ Verification script not found, skipping verification"
fi

echo ""
echo "🎉 Validatus production setup completed!"
echo ""
echo "Your application is now running on GCP with full database persistence!"
echo ""
echo "📋 Quick Links:"
echo "• Application: https://validatus-backend-ssivkqhvhq-uc.a.run.app"
echo "• Health Check: https://validatus-backend-ssivkqhvhq-uc.a.run.app/health"
echo "• API Docs: https://validatus-backend-ssivkqhvhq-uc.a.run.app/docs"
echo ""
echo "🔧 Next Steps:"
echo "1. Configure your frontend to use the new backend URL"
echo "2. Set up custom domain and SSL certificates"
echo "3. Configure monitoring and alerting"
echo "4. Set up backup and disaster recovery procedures"
echo ""
echo "🌐 Your Validatus platform is ready for production use!"
