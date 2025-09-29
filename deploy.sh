#!/bin/bash
# deploy.sh

set -e

PROJECT_ID="validatus-platform"
REGION="us-central1"

echo "🚀 Deploying Validatus to GCP..."

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    firestore.googleapis.com \
    pubsub.googleapis.com \
    monitoring.googleapis.com \
    cloudtasks.googleapis.com \
    cloudfunctions.googleapis.com \
    logging.googleapis.com \
    clouderrorreporting.googleapis.com \
    memcache.googleapis.com

# Create Cloud SQL instance if it doesn't exist
echo "🗄️ Setting up Cloud SQL..."
if ! gcloud sql instances describe validatus-sql --project=$PROJECT_ID &>/dev/null; then
    gcloud sql instances create validatus-sql \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password="$(openssl rand -base64 32)"
fi

# Create database
gcloud sql databases create validatusdb --instance=validatus-sql --project=$PROJECT_ID || true

# Store database password in Secret Manager
echo "🔐 Setting up secrets..."
if ! gcloud secrets describe validatus-db-password --project=$PROJECT_ID &>/dev/null; then
    echo -n "$(openssl rand -base64 32)" | \
        gcloud secrets create validatus-db-password --data-file=- --project=$PROJECT_ID
fi

# Create service account
echo "👤 Setting up service account..."
gcloud iam service-accounts create validatus-run \
    --display-name="Validatus Cloud Run SA" \
    --project=$PROJECT_ID || true

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:validatus-run@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:validatus-run@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:validatus-run@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:validatus-run@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Trigger build
echo "🔨 Triggering Cloud Build..."
gcloud builds submit --config cloudbuild.yaml --project=$PROJECT_ID .

echo "✅ Deployment completed!"
echo "🌐 Frontend URL: https://validatus-frontend-$(gcloud config get-value project).run.app"
echo "🔧 Backend URL: https://validatus-backend-$(gcloud config get-value project).run.app"
