#!/bin/bash

set -e

# Configuration
PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
ENVIRONMENT="${3:-}"
TERRAFORM_DIR="infrastructure/terraform"

if [ -z "$PROJECT_ID" ] || [ -z "$ENVIRONMENT" ]; then
    echo "❌ Usage: $0 <PROJECT_ID> <ENVIRONMENT> [REGION]"
    echo "   Example: $0 validatus-platform development us-central1"
    echo "   Environment options: development, staging, production"
    exit 1
fi

echo "🚀 Setting up GCP Infrastructure for Validatus..."
echo "Project ID: $PROJECT_ID"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo ""

# Check if required tools are installed
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    if ! command -v gcloud &> /dev/null; then
        echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
        exit 1
    fi
    
    if ! command -v terraform &> /dev/null; then
        echo "❌ Terraform not found. Please install Terraform."
        exit 1
    fi
    
    echo "✅ Dependencies check passed"
}

# Authenticate with Google Cloud
setup_gcloud() {
    echo "🔐 Setting up Google Cloud authentication..."
    
    # Check if already authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        echo "Please authenticate with Google Cloud:"
        gcloud auth login
    fi
    
    # Set the project
    gcloud config set project $PROJECT_ID
    
    # Enable Application Default Credentials
    gcloud auth application-default login
    
    echo "✅ Google Cloud authentication setup complete"
}

# Initialize Terraform
setup_terraform() {
    echo "🏗️ Initializing Terraform..."
    
    cd $TERRAFORM_DIR
    
    # Initialize Terraform
    terraform init
    
    # Validate configuration
    terraform validate
    
    echo "✅ Terraform initialized successfully"
}

# Setup Terraform backend
setup_terraform_backend() {
    echo "🪣 Setting up Terraform backend..."
    
    # Run the backend setup script
    ../../scripts/setup-terraform-backend.sh "$PROJECT_ID"
    
    echo "✅ Terraform backend setup completed"
}

# Plan and apply infrastructure
deploy_infrastructure() {
    echo "📋 Planning infrastructure deployment..."
    
    # Generate Terraform plan with required variables
    terraform plan \
        -var="project_id=$PROJECT_ID" \
        -var="region=$REGION" \
        -var="environment=$ENVIRONMENT" \
        -out=tfplan
    
    # Check for non-interactive mode
    if [ "${AUTO_APPROVE:-false}" = "true" ]; then
        echo "🚀 Auto-approve enabled, applying Terraform plan..."
        terraform apply tfplan
        echo "✅ Infrastructure deployment completed successfully!"
        rm -f tfplan
        return
    fi
    
    echo ""
    echo "📊 Terraform plan generated. Review the plan above."
    echo ""
    read -p "Do you want to proceed with infrastructure deployment? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Applying Terraform plan..."
        terraform apply tfplan
        echo "✅ Infrastructure deployment completed successfully!"
    else
        echo "⏸️ Infrastructure deployment cancelled."
        rm -f tfplan
        exit 0
    fi
    
    # Clean up plan file
    rm -f tfplan
}

# Generate environment configuration
generate_env_config() {
    echo "📝 Generating environment configuration..."
    
    # Extract Terraform outputs
    terraform output -json > outputs.json
    
    # Generate .env file from outputs
    cat > "../../backend/.env.production" << EOF
# Generated GCP Environment Configuration
# Generated on: $(date)

# GCP Project Configuration
GCP_PROJECT_ID=$PROJECT_ID
GCP_REGION=$REGION
GCP_ZONE=${REGION}-a
ENVIRONMENT=production

# Cloud SQL Configuration
CLOUD_SQL_CONNECTION_NAME=$(terraform output -raw cloud_sql_connection_name)
CLOUD_SQL_DATABASE=$(terraform output -raw database_name)
CLOUD_SQL_USER=$(terraform output -raw database_user)
CLOUD_SQL_PASSWORD_SECRET=cloud-sql-password

# Cloud Storage Configuration
CONTENT_STORAGE_BUCKET=$(terraform output -raw content_bucket_name)
EMBEDDINGS_STORAGE_BUCKET=$(terraform output -raw embeddings_bucket_name)
REPORTS_STORAGE_BUCKET=$(terraform output -raw reports_bucket_name)

# Vertex AI Configuration
VECTOR_SEARCH_LOCATION=$REGION
EMBEDDING_MODEL=text-embedding-004
VECTOR_DIMENSIONS=768

# Memorystore Redis Configuration
REDIS_HOST=$(terraform output -raw redis_host)
REDIS_PORT=$(terraform output -raw redis_port)

# Cloud Spanner Configuration
SPANNER_INSTANCE_ID=$(terraform output -raw spanner_instance_id)
SPANNER_DATABASE_ID=$(terraform output -raw spanner_database_id)

# Service Account Configuration
SERVICE_ACCOUNT_EMAIL=$(terraform output -raw service_account_email)

# Application Configuration
LOCAL_DEVELOPMENT_MODE=false
USE_IAM_AUTH=true
MAX_CONCURRENT_OPERATIONS=50
CONNECTION_POOL_SIZE=20
QUERY_TIMEOUT_SECONDS=30

# Performance Configuration
ENABLE_CACHING=true
CACHE_TTL=3600

# Monitoring Configuration
ENABLE_MONITORING=true
LOG_LEVEL=INFO
EOF

    echo "✅ Environment configuration generated: backend/.env.production"
    
    # Validate Secret Manager secrets
    echo "Validating Secret Manager secrets..."
    if ! gcloud secrets describe cloud-sql-password --project="$PROJECT_ID" &>/dev/null; then
        echo "❌ Required secret 'cloud-sql-password' not found in Secret Manager"
        echo "Please create it with: gcloud secrets create cloud-sql-password --data-file=<password-file>"
        exit 1
    fi
    echo "✅ Required secrets validated"
    
    # Clean up
    rm -f outputs.json
}

# Setup database schema
setup_database() {
    echo "🗄️ Setting up database schema..."
    
    cd ../../backend
    
    # Install dependencies if not already installed
    if [ ! -d "venv" ]; then
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements-gcp.txt
    else
        source venv/bin/activate
    fi
    
    # Run database migrations
    # Load environment variables safely
    source ../scripts/load-env.sh
    load_env_file .env.production
    python -c "
import asyncio
from app.services.gcp_persistence_manager import get_gcp_persistence_manager

async def setup_db():
    manager = get_gcp_persistence_manager()
    await manager.initialize()
    print('✅ Database schema setup completed')
    await manager.close()

asyncio.run(setup_db())
"
    
    deactivate
    cd ../infrastructure/terraform
}

# Verify deployment
verify_deployment() {
    echo "🧪 Verifying deployment..."
    
    # Test Cloud SQL connection
    echo "Testing Cloud SQL connection..."
    if gcloud sql connect validatus-primary --user=validatus_app --quiet; then
        echo "✅ Cloud SQL connection successful"
    else
        echo "❌ Cloud SQL connection failed"
    fi
    
    # Test storage buckets
    echo "Testing Cloud Storage buckets..."
    CONTENT_BUCKET=$(terraform output -raw content_bucket_name)
    if gsutil ls gs://$CONTENT_BUCKET > /dev/null 2>&1; then
        echo "✅ Cloud Storage buckets accessible"
    else
        echo "❌ Cloud Storage buckets not accessible"
    fi
    
    # Test Redis connection
    echo "Testing Redis connection..."
    REDIS_HOST=$(terraform output -raw redis_host)
    if timeout 5 bash -c "</dev/tcp/$REDIS_HOST/6379" 2>/dev/null; then
        echo "✅ Redis connection successful"
    else
        echo "❌ Redis connection failed"
    fi
    
    echo "✅ Deployment verification completed"
}

# Main execution
main() {
    echo "🎯 Validatus GCP Infrastructure Setup"
    echo "======================================"
    
    check_dependencies
    setup_gcloud
    setup_terraform_backend
    setup_terraform
    deploy_infrastructure
    generate_env_config
    setup_database
    verify_deployment
    
    echo ""
    echo "🎉 GCP Infrastructure setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Review the generated .env.production file"
    echo "2. Deploy your application using: gcloud run deploy"
    echo "3. Configure your domain and SSL certificates"
    echo "4. Set up monitoring and alerting"
    echo ""
    echo "🌐 Your Validatus infrastructure is ready for production!"
}

# Run the main function
main "$@"
