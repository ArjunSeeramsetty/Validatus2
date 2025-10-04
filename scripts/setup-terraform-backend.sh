#!/bin/bash
set -euo pipefail

# Setup Terraform GCS Backend
# This script creates the GCS bucket for Terraform state storage

PROJECT_ID="${1:-}"
BUCKET_NAME="${2:-validatus-terraform-state}"
BUCKET_LOCATION="${3:-us-central1}"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Usage: $0 <PROJECT_ID> [BUCKET_NAME] [BUCKET_LOCATION]"
    echo "   Example: $0 validatus-platform validatus-terraform-state us-central1"
    exit 1
fi

echo "🚀 Setting up Terraform GCS Backend"
echo "=================================="
echo "Project ID: $PROJECT_ID"
echo "Bucket Name: $BUCKET_NAME"
echo "Bucket Location: $BUCKET_LOCATION"
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ Please authenticate with Google Cloud:"
    echo "   gcloud auth login"
    echo "   gcloud auth application-default login"
    exit 1
fi

# Set the project
echo "🔧 Setting project..."
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable storage-api.googleapis.com

# Create the bucket with versioning and lifecycle
echo "🪣 Creating GCS bucket for Terraform state..."
if gsutil ls -b "gs://$BUCKET_NAME" >/dev/null 2>&1; then
    echo "✅ Bucket $BUCKET_NAME already exists"
else
    # Create bucket with versioning and lifecycle
    gsutil mb -l "$BUCKET_LOCATION" "gs://$BUCKET_NAME"
    
    # Enable versioning for state safety
    gsutil versioning set on "gs://$BUCKET_NAME"
    
    # Set lifecycle policy to manage old versions
    cat > /tmp/lifecycle.json << EOF
{
  "rule": [
    {
      "action": {
        "type": "SetStorageClass",
        "storageClass": "NEARLINE"
      },
      "condition": {
        "age": 30
      }
    },
    {
      "action": {
        "type": "SetStorageClass",
        "storageClass": "COLDLINE"
      },
      "condition": {
        "age": 90
      }
    },
    {
      "action": {
        "type": "Delete"
      },
      "condition": {
        "age": 365
      }
    }
  ]
}
EOF
    
    gsutil lifecycle set /tmp/lifecycle.json "gs://$BUCKET_NAME"
    rm /tmp/lifecycle.json
    
    echo "✅ Bucket $BUCKET_NAME created with versioning and lifecycle"
fi

# Set bucket permissions for Terraform
echo "🔐 Setting bucket permissions..."
# Allow the current user to read/write
USER_EMAIL=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
gsutil iam ch "user:$USER_EMAIL:objectAdmin" "gs://$BUCKET_NAME"

# Allow Cloud Build service account (if it exists)
CLOUD_BUILD_SA="${PROJECT_ID}@cloudbuild.gserviceaccount.com"
if gcloud iam service-accounts describe "$CLOUD_BUILD_SA" >/dev/null 2>&1; then
    gsutil iam ch "serviceAccount:$CLOUD_BUILD_SA:objectAdmin" "gs://$BUCKET_NAME"
    echo "✅ Added Cloud Build service account permissions"
fi

echo ""
echo "🎉 Terraform backend setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Create terraform.tfvars file:"
echo "   cp terraform.tfvars.example terraform.tfvars"
echo "   # Edit terraform.tfvars with your values"
echo ""
echo "2. Initialize Terraform:"
echo "   cd infrastructure/terraform"
echo "   terraform init"
echo ""
echo "3. Plan and apply:"
echo "   terraform plan -var-file=terraform.tfvars"
echo "   terraform apply -var-file=terraform.tfvars"
echo ""
echo "🔗 Backend Configuration:"
echo "   Bucket: gs://$BUCKET_NAME"
echo "   Prefix: terraform/state"
