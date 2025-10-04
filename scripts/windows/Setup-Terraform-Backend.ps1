<#
.SYNOPSIS
    Setup Terraform GCS Backend for Validatus infrastructure

.DESCRIPTION
    This script creates the GCS bucket for Terraform state storage with proper
    versioning, lifecycle policies, and permissions.

.PARAMETER ProjectId
    GCP Project ID (required)

.PARAMETER BucketName
    GCS Bucket name for Terraform state (optional, defaults to validatus-terraform-state)

.EXAMPLE
    .\Setup-Terraform-Backend.ps1 -ProjectId "validatus-platform"

.EXAMPLE
    .\Setup-Terraform-Backend.ps1 -ProjectId "validatus-platform" -BucketName "my-terraform-state"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory = $false)]
    [string]$BucketName = "validatus-terraform-state"
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Terraform GCS Backend" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Project ID: $ProjectId" -ForegroundColor Yellow
Write-Host "Bucket Name: $BucketName" -ForegroundColor Yellow
Write-Host ""

# Check if gcloud is authenticated
Write-Host "🔍 Checking Google Cloud authentication..." -ForegroundColor Cyan
try {
    $authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if (-not $authCheck) {
        Write-Host "❌ Please authenticate with Google Cloud:" -ForegroundColor Red
        Write-Host "   gcloud auth login" -ForegroundColor Yellow
        Write-Host "   gcloud auth application-default login" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Authenticated as: $authCheck" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to check authentication: $_" -ForegroundColor Red
    exit 1
}

# Set the project
Write-Host "🔧 Setting project..." -ForegroundColor Cyan
try {
    gcloud config set project $ProjectId
    Write-Host "✅ Project set to: $ProjectId" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to set project: $_" -ForegroundColor Red
    exit 1
}

# Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor Cyan
try {
    gcloud services enable storage-api.googleapis.com
    Write-Host "✅ Storage API enabled" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to enable APIs: $_" -ForegroundColor Red
    exit 1
}

# Create the bucket with versioning and lifecycle
Write-Host "🪣 Creating GCS bucket for Terraform state..." -ForegroundColor Cyan
try {
    $bucketExists = gsutil ls -b "gs://$BucketName" 2>$null
    if ($bucketExists) {
        Write-Host "✅ Bucket $BucketName already exists" -ForegroundColor Green
    } else {
        # Create bucket
        gsutil mb -l us-central1 "gs://$BucketName"
        
        # Enable versioning
        gsutil versioning set on "gs://$BucketName"
        
        # Set lifecycle policy
        $lifecyclePolicy = @"
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
    }
  ]
}
"@
        
        $tempFile = [System.IO.Path]::GetTempFileName()
        $lifecyclePolicy | Out-File -FilePath $tempFile -Encoding UTF8
        
        gsutil lifecycle set $tempFile "gs://$BucketName"
        Remove-Item $tempFile
        
        Write-Host "✅ Bucket $BucketName created with versioning and lifecycle" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to create bucket: $_" -ForegroundColor Red
    exit 1
}

# Set bucket permissions
Write-Host "🔐 Setting bucket permissions..." -ForegroundColor Cyan
try {
    # Get current user email
    $userEmail = gcloud auth list --filter=status:ACTIVE --format="value(account)"
    
    # Allow the current user to read/write
    gsutil iam ch "user:$userEmail:objectAdmin" "gs://$BucketName"
    Write-Host "✅ Added user permissions: $userEmail" -ForegroundColor Green
    
    # Allow Cloud Build service account (if it exists)
    $cloudBuildSA = "${ProjectId}@cloudbuild.gserviceaccount.com"
    try {
        gcloud iam service-accounts describe $cloudBuildSA 2>&1 | Out-Null
        gsutil iam ch "serviceAccount:$cloudBuildSA:objectAdmin" "gs://$BucketName"
        Write-Host "✅ Added Cloud Build service account permissions" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Cloud Build service account not found (will be created later)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to set permissions: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Terraform backend setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Create terraform.tfvars file:" -ForegroundColor White
Write-Host "   Copy-Item terraform.tfvars.example terraform.tfvars" -ForegroundColor Gray
Write-Host "   # Edit terraform.tfvars with your values" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Initialize Terraform:" -ForegroundColor White
Write-Host "   cd infrastructure/terraform" -ForegroundColor Gray
Write-Host "   terraform init" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Plan and apply:" -ForegroundColor White
Write-Host "   terraform plan -var-file=terraform.tfvars" -ForegroundColor Gray
Write-Host "   terraform apply -var-file=terraform.tfvars" -ForegroundColor Gray
Write-Host ""
Write-Host "🔗 Backend Configuration:" -ForegroundColor Cyan
Write-Host "   Bucket: gs://$BucketName" -ForegroundColor White
Write-Host "   Prefix: terraform/state" -ForegroundColor White
