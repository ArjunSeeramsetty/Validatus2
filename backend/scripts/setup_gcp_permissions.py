#!/usr/bin/env python3
"""
Setup GCP Permissions and Secrets for Validatus2
"""
import os
import subprocess
import json

def run_command(command, description=""):
    """Run a shell command and return result"""
    print(f"🔧 {description}")
    print(f"   Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"   ✅ Success")
        return result.stdout
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return None

def setup_gcp_permissions():
    """Setup all required GCP permissions and secrets"""
    
    project_id = os.getenv("GCP_PROJECT_ID", "validatus-platform")
    service_account_email = f"validatus-backend@{project_id}.iam.gserviceaccount.com"
    
    print(f"🚀 Setting up GCP permissions for project: {project_id}")
    print("=" * 60)
    
    # Step 1: Enable required APIs
    apis = [
        "cloudsql.googleapis.com",
        "secretmanager.googleapis.com",
        "run.googleapis.com",
        "cloudbuild.googleapis.com"
    ]
    
    for api in apis:
        run_command(
            f"gcloud services enable {api} --project={project_id}",
            f"Enabling {api}"
        )
    
    # Step 2: Create service account if it doesn't exist
    run_command(
        f"gcloud iam service-accounts create validatus-backend --project={project_id} --display-name='Validatus Backend Service Account' || true",
        "Creating service account"
    )
    
    # Step 3: Grant required IAM roles
    roles = [
        "roles/cloudsql.client",
        "roles/secretmanager.secretAccessor",
        "roles/logging.logWriter",
        "roles/monitoring.metricWriter"
    ]
    
    for role in roles:
        run_command(
            f"gcloud projects add-iam-policy-binding {project_id} --member='serviceAccount:{service_account_email}' --role='{role}'",
            f"Granting {role}"
        )
    
    # Step 4: Create database password secret
    db_password = input("Enter Cloud SQL password (or press Enter to generate): ").strip()
    if not db_password:
        db_password = os.urandom(16).hex()
        print(f"Generated password: {db_password}")
    
    # Create secret
    run_command(
        f"echo '{db_password}' | gcloud secrets create cloud-sql-password --data-file=- --project={project_id} || true",
        "Creating database password secret"
    )
    
    # Step 5: Grant secret access
    run_command(
        f"gcloud secrets add-iam-policy-binding cloud-sql-password --member='serviceAccount:{service_account_email}' --role='roles/secretmanager.secretAccessor' --project={project_id}",
        "Granting secret access"
    )
    
    # Step 6: Update Cloud SQL user password
    run_command(
        f"gcloud sql users set-password validatus_app --instance=validatus-sql --password='{db_password}' --project={project_id}",
        "Updating Cloud SQL user password"
    )
    
    print("\n🎉 GCP permissions setup completed!")
    print(f"✅ Service account: {service_account_email}")
    print(f"✅ Database password stored in Secret Manager")
    print(f"✅ All required permissions granted")

if __name__ == "__main__":
    setup_gcp_permissions()
