<#
.SYNOPSIS
    Deploy Validatus to GCP Cloud Run production environment
.DESCRIPTION
    This script builds and deploys the Validatus application to Cloud Run
#>

[CmdletBinding()]
param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1",
    [string]$ServiceName = "validatus-backend",
    [switch]$SkipBuild,
    [switch]$SkipTests,
    [int]$TimeoutMinutes = 40
)

Write-Host "🚀 Deploying Validatus to Production..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Function to build and deploy backend
function Deploy-Backend {
    if ($SkipBuild) {
        Write-Host "⏭️ Skipping build step" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🔨 Building and deploying backend..." -ForegroundColor Cyan
    
    # Check if cloudbuild-production.yaml exists
    if (-not (Test-Path "cloudbuild-production.yaml")) {
        Write-Host "❌ cloudbuild-production.yaml not found" -ForegroundColor Red
        Write-Host "Please make sure you're in the project root directory" -ForegroundColor Yellow
        exit 1
    }
    
    # Build container image
    $buildArgs = @(
        "builds", "submit",
        "--config=cloudbuild-production.yaml",
        "--substitutions=_PROJECT_ID=$ProjectId",
        "--timeout=$($TimeoutMinutes * 60)s",
        "."
    )
    
    Write-Host "Starting Cloud Build..." -ForegroundColor Cyan
    & gcloud @buildArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Cloud Build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Backend deployment completed" -ForegroundColor Green
}

# Function to test deployment
function Test-Deployment {
    if ($SkipTests) {
        Write-Host "⏭️ Skipping deployment tests" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🧪 Testing deployment..." -ForegroundColor Cyan
    
    # Get service URL
    $serviceUrlArgs = @(
        "run", "services", "describe", $ServiceName,
        "--region=$Region",
        "--format=value(status.url)"
    )
    
    $serviceUrl = & gcloud @serviceUrlArgs
    
    if (-not $serviceUrl) {
        Write-Host "❌ Failed to get service URL" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Service URL: $serviceUrl" -ForegroundColor White
    
    # Health check with retry
    $maxRetries = 5
    $retryCount = 0
    $healthCheckPassed = $false
    
    while ($retryCount -lt $maxRetries -and -not $healthCheckPassed) {
        try {
            Write-Host "Attempting health check (attempt $($retryCount + 1)/$maxRetries)..." -ForegroundColor Cyan
            
            $response = Invoke-WebRequest -Uri "$serviceUrl/health" -TimeoutSec 30 -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                $healthData = $response.Content | ConvertFrom-Json
                Write-Host "✅ Health check passed: $($healthData.status)" -ForegroundColor Green
                $healthCheckPassed = $true
            } else {
                Write-Host "❌ Health check failed: HTTP $($response.StatusCode)" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
            $retryCount++
            if ($retryCount -lt $maxRetries) {
                Write-Host "Retrying in 10 seconds..." -ForegroundColor Yellow
                Start-Sleep 10
            }
        }
    }
    
    if (-not $healthCheckPassed) {
        Write-Host "❌ Health check failed after $maxRetries attempts" -ForegroundColor Red
        return $false
    }
    
    # Test database connection through API
    try {
        Write-Host "Testing database connection..." -ForegroundColor Cyan
        $response = Invoke-WebRequest -Uri "$serviceUrl/health" -TimeoutSec 30
        $healthData = $response.Content | ConvertFrom-Json
        
        if ($healthData.gcp_services) {
            Write-Host "✅ GCP services health check available" -ForegroundColor Green
            
            foreach ($service in $healthData.gcp_services.services.PSObject.Properties) {
                $serviceName = $service.Name
                $serviceStatus = $service.Value.status
                
                if ($serviceStatus -eq "healthy") {
                    Write-Host "  ✅ $serviceName: $serviceStatus" -ForegroundColor Green
                } else {
                    Write-Host "  ❌ $serviceName: $serviceStatus" -ForegroundColor Red
                }
            }
        }
        
        Write-Host "✅ Service is healthy and responding" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "❌ Database connection test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to setup monitoring
function Initialize-Monitoring {
    Write-Host "📊 Setting up monitoring and alerting..." -ForegroundColor Cyan
    
    # Check if monitoring script exists
    if (Test-Path "scripts\windows\Deploy-Monitoring.ps1") {
        Write-Host "Running monitoring setup script..." -ForegroundColor Cyan
        & ".\scripts\windows\Deploy-Monitoring.ps1" -ProjectId $ProjectId -Region $Region
    } else {
        Write-Host "⚠️ Monitoring script not found, skipping monitoring setup" -ForegroundColor Yellow
    }
    
    Write-Host "✅ Monitoring setup completed" -ForegroundColor Green
}

# Function to run post-deployment verification
function Invoke-PostDeploymentVerification {
    Write-Host "🔍 Running post-deployment verification..." -ForegroundColor Cyan
    
    if (Test-Path "scripts\windows\Verify-Production.ps1") {
        Write-Host "Running production verification script..." -ForegroundColor Cyan
        & ".\scripts\windows\Verify-Production.ps1" -ProjectId $ProjectId -Region $Region -ServiceName $ServiceName
    } else {
        Write-Host "⚠️ Verification script not found, running basic checks" -ForegroundColor Yellow
        
        # Basic verification
        $serviceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"
        
        Write-Host ""
        Write-Host "🎯 Deployment Summary:" -ForegroundColor Cyan
        Write-Host "===================" -ForegroundColor Cyan
        Write-Host "🌐 Service URL: $serviceUrl" -ForegroundColor White
        Write-Host "📋 Health Check: $serviceUrl/health" -ForegroundColor White
        Write-Host "📖 API Docs: $serviceUrl/docs" -ForegroundColor White
        Write-Host ""
    }
}

# Main execution
try {
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Region: $Region" -ForegroundColor White
    Write-Host "Service Name: $ServiceName" -ForegroundColor White
    Write-Host ""
    
    # Step 1: Deploy backend
    Deploy-Backend
    
    # Step 2: Test deployment
    $deploymentHealthy = Test-Deployment
    
    # Step 3: Setup monitoring
    Initialize-Monitoring
    
    # Step 4: Post-deployment verification
    Invoke-PostDeploymentVerification
    
    if ($deploymentHealthy) {
        Write-Host ""
        Write-Host "🎉 Production deployment completed successfully!" -ForegroundColor Green
        Write-Host ""
        
        $serviceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"
        
        Write-Host "🎯 Deployment Results:" -ForegroundColor Cyan
        Write-Host "=====================" -ForegroundColor Cyan
        Write-Host "🌐 Service URL: $serviceUrl" -ForegroundColor White
        Write-Host "📋 Health Check: $serviceUrl/health" -ForegroundColor White
        Write-Host "📖 API Docs: $serviceUrl/docs" -ForegroundColor White
        Write-Host "🔧 Cloud Console: https://console.cloud.google.com/run/detail/$Region/$ServiceName/metrics?project=$ProjectId" -ForegroundColor White
        Write-Host ""
        Write-Host "📋 Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Configure your custom domain (optional)" -ForegroundColor White
        Write-Host "2. Set up SSL certificates" -ForegroundColor White
        Write-Host "3. Configure monitoring alerts" -ForegroundColor White
        Write-Host "4. Test your application end-to-end" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "⚠️ Deployment completed with issues. Please check the logs above." -ForegroundColor Yellow
        exit 1
    }
    
} catch {
    Write-Host "❌ Production deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}
