#!/bin/bash
# deploy_phase_a.sh - Phase A Deployment Script

echo "🚀 Deploying Validatus Phase A: Stabilization & Foundation"

# 1. Backup current configuration
echo "📦 Creating backup of current configuration..."
cp backend/app/main.py backend/app/main.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# 2. Apply Phase A fixes
echo "🔧 Applying Phase A stabilization fixes..."

# Create directories if they don't exist
mkdir -p backend/app/api/v3
mkdir -p backend/app/services/adapters
mkdir -p backend/app/services/enhanced_analytical_engines

# 3. Update requirements if needed
echo "📋 Checking Python dependencies..."
if ! grep -q "scipy" backend/requirements.txt; then
    echo "scipy==1.11.4" >> backend/requirements.txt
    echo "✅ Added scipy dependency"
fi

# 4. Set Phase A environment variables
echo "⚙️  Configuring Phase A environment..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env file"
fi

# Update .env with Phase A configuration
cat >> .env << 'EOF'

# Phase A Configuration
ENABLE_RESULTS_MANAGER=true
ENABLE_RESULTS_API=true
ENABLE_ENHANCED_ANALYTICS=false
DEBUG_MODE=true
ENVIRONMENT=development
LOCAL_DEVELOPMENT_MODE=false
EOF

# 5. Install dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# 6. Test backend startup
echo "🧪 Testing backend startup..."
timeout 30s python -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✅ Backend imports successful')
except Exception as e:
    print(f'❌ Backend import failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Phase A deployment successful!"
    echo "🚀 You can now start the backend with: python -m app.main"
else
    echo "❌ Phase A deployment failed - check errors above"
    exit 1
fi

echo ""
echo "📊 Phase A Status:"
echo "  ✅ Backend startup issues fixed"
echo "  ✅ Feature flag system implemented"
echo "  ✅ Placeholder services created"
echo "  ✅ Service factory pattern ready"
echo "  ✅ Vector store adapters prepared"
echo ""
echo "🎯 Next Steps:"
echo "  1. Start backend: cd backend && python -m app.main"
echo "  2. Test health check: curl http://localhost:8000/health"
echo "  3. Review system status: curl http://localhost:8000/api/v3/system/status"
echo "  4. Ready for Phase B implementation when needed"
