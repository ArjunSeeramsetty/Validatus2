#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Export API keys to Google Secret Manager for Validatus platform

.DESCRIPTION
    This script exports all API keys from environment variables to Google Secret Manager
    for secure storage and retrieval by the application.

.PARAMETER ProjectId
    GCP Project ID (default: validatus-platform)

.PARAMETER Region
    GCP Region (default: us-central1)

.EXAMPLE
    .\Export-API-Keys-To-SecretManager.ps1
    .\Export-API-Keys-To-SecretManager.ps1 -ProjectId "my-project" -Region "us-east1"
#>

param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1"
)

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "🔐 Exporting API keys to Google Secret Manager..." -ForegroundColor Green
Write-Host "Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan

# Function to create or update secret
function Set-GoogleSecret {
    param(
        [string]$SecretName,
        [string]$SecretValue,
        [string]$ProjectId
    )
    
    try {
        # Check if secret exists
        $existingSecret = gcloud secrets describe $SecretName --project=$ProjectId 2>$null
        
        if ($existingSecret) {
            Write-Host "  Updating existing secret: $SecretName" -ForegroundColor Yellow
            
            # Create new version of existing secret
            $tempFile = [System.IO.Path]::GetTempFileName()
            $SecretValue | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
            
            gcloud secrets versions add $SecretName --data-file=$tempFile --project=$ProjectId
            
            Remove-Item $tempFile -Force
        } else {
            Write-Host "  Creating new secret: $SecretName" -ForegroundColor Green
            
            # Create new secret
            $tempFile = [System.IO.Path]::GetTempFileName()
            $SecretValue | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
            
            gcloud secrets create $SecretName --data-file=$tempFile --project=$ProjectId
            
            Remove-Item $tempFile -Force
            
            # Add IAM policy for the service account
            $serviceAccount = "validatus-run@$ProjectId.iam.gserviceaccount.com"
            gcloud secrets add-iam-policy-binding $SecretName --member="serviceAccount:$serviceAccount" --role="roles/secretmanager.secretAccessor" --project=$ProjectId
        }
        
        Write-Host "  ✅ Secret $SecretName processed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Failed to process secret $SecretName : $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
}

try {
    # Enable required APIs
    Write-Host "🔧 Enabling Secret Manager API..." -ForegroundColor Yellow
    gcloud services enable secretmanager.googleapis.com --project=$ProjectId

    # Export each API key from environment variables
    Write-Host "📤 Exporting API keys to Secret Manager..." -ForegroundColor Yellow
    
    # Define API key environment variable mappings
    $apiKeyMappings = @{
        "perplexity-api-key" = "PERPLEXITY_API_KEY"
        "openai-api-key" = "OPENAI_API_KEY"
        "tavily-api-key" = "TAVILY_API_KEY"
        "anthropic-api-key" = "ANTHROPIC_API_KEY"
        "google-gemini-api-key" = "GOOGLE_GEMINI_API_KEY"
        "google-search-api-key" = "GOOGLE_SEARCH_API_KEY"
        "google-search-engine-id" = "GOOGLE_SEARCH_ENGINE_ID"
        "huggingface-access-key" = "HUGGINGFACE_ACCESS_KEY"
        "google-cse-api-key" = "GOOGLE_CSE_API_KEY"
        "google-cse-id" = "GOOGLE_CSE_ID"
    }

    foreach ($secretName in $apiKeyMappings.Keys) {
        $envVarName = $apiKeyMappings[$secretName]
        $apiKeyValue = [Environment]::GetEnvironmentVariable($envVarName)
        
        if ($apiKeyValue) {
            Set-GoogleSecret -SecretName $secretName -SecretValue $apiKeyValue -ProjectId $ProjectId
        } else {
            Write-Host "  ⚠️  Environment variable $envVarName not set, skipping $secretName" -ForegroundColor Yellow
        }
    }

    Write-Host "✅ All API keys exported successfully to Google Secret Manager!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Exported secrets:" -ForegroundColor Cyan
    foreach ($secretName in $apiKeyMappings.Keys) {
        Write-Host "  - $secretName" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "🔍 You can verify the secrets using:" -ForegroundColor Cyan
    Write-Host "  gcloud secrets list --project=$ProjectId" -ForegroundColor White
    Write-Host ""
    Write-Host "🔐 To access a secret value:" -ForegroundColor Cyan
    Write-Host "  gcloud secrets versions access latest --secret=SECRET_NAME --project=$ProjectId" -ForegroundColor White

} catch {
    Write-Host "❌ Error exporting API keys: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}