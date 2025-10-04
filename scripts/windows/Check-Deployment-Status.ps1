<#
.SYNOPSIS
    Quick deployment status checker for Validatus
.DESCRIPTION
    This script provides a quick overview of the current deployment status
#>

[CmdletBinding()]
param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1",
    [string]$ServiceName = "validatus-backend"
)

Write-Host "🔍 Validatus Deployment Status Check" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

$ErrorActionPreference = "SilentlyContinue"

# Function to check tool availability
function Test-ToolAvailability {
    param([string]$ToolName, [string]$Command)
    
    try {
        $version = Invoke-Expression $Command 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $ToolName : Available" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $ToolName : Not available" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ $ToolName : Not available" -ForegroundColor Red
        return $false
    }
}

# Function to check GCP authentication
function Test-GCPAuthentication {
    try {
        $account = gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>$null
        if ($account) {
            Write-Host "✅ GCP Authentication : $account" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ GCP Authentication : Not authenticated" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ GCP Authentication : Not available" -ForegroundColor Red
        return $false
    }
}

# Function to check project configuration
function Test-ProjectConfiguration {
    try {
        $currentProject = gcloud config get-value project 2>$null
        if ($currentProject -eq $ProjectId) {
            Write-Host "✅ GCP Project : $currentProject" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ GCP Project : $currentProject (expected: $ProjectId)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ GCP Project : Not configured" -ForegroundColor Red
        return $false
    }
}

# Function to check infrastructure status
function Test-InfrastructureStatus {
    Write-Host "`n🏗️ Infrastructure Status" -ForegroundColor Cyan
    Write-Host "------------------------" -ForegroundColor Cyan
    
    $infrastructureHealthy = $true
    
    # Check Cloud SQL
    try {
        $sqlInstances = gcloud sql instances list --filter="name:validatus-primary" --format="value(name)" 2>$null
        if ($sqlInstances) {
            Write-Host "✅ Cloud SQL : validatus-primary exists" -ForegroundColor Green
        } else {
            Write-Host "❌ Cloud SQL : validatus-primary not found" -ForegroundColor Red
            $infrastructureHealthy = $false
        }
    } catch {
        Write-Host "❌ Cloud SQL : Check failed" -ForegroundColor Red
        $infrastructureHealthy = $false
    }
    
    # Check Cloud Storage
    try {
        $buckets = gsutil ls 2>$null | Select-String "validatus"
        if ($buckets) {
            Write-Host "✅ Cloud Storage : Buckets found" -ForegroundColor Green
        } else {
            Write-Host "❌ Cloud Storage : No buckets found" -ForegroundColor Red
            $infrastructureHealthy = $false
        }
    } catch {
        Write-Host "❌ Cloud Storage : Check failed" -ForegroundColor Red
        $infrastructureHealthy = $false
    }
    
    # Check Redis
    try {
        $redisInstances = gcloud redis instances list --filter="name:validatus-cache" --format="value(name)" 2>$null
        if ($redisInstances) {
            Write-Host "✅ Redis : validatus-cache exists" -ForegroundColor Green
        } else {
            Write-Host "❌ Redis : validatus-cache not found" -ForegroundColor Red
            $infrastructureHealthy = $false
        }
    } catch {
        Write-Host "❌ Redis : Check failed" -ForegroundColor Red
        $infrastructureHealthy = $false
    }
    
    return $infrastructureHealthy
}

# Function to check application status
function Test-ApplicationStatus {
    Write-Host "`n🚀 Application Status" -ForegroundColor Cyan
    Write-Host "---------------------" -ForegroundColor Cyan
    
    try {
        $serviceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)" 2>$null
        
        if ($serviceUrl) {
            Write-Host "✅ Cloud Run Service : $ServiceName deployed" -ForegroundColor Green
            Write-Host "   URL: $serviceUrl" -ForegroundColor Gray
            
            # Test health endpoint
            try {
                $response = Invoke-WebRequest -Uri "$serviceUrl/health" -TimeoutSec 10 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    $healthData = $response.Content | ConvertFrom-Json
                    if ($healthData.status -eq "healthy") {
                        Write-Host "✅ Application Health : Healthy" -ForegroundColor Green
                        return $true
                    } else {
                        Write-Host "⚠️ Application Health : $($healthData.status)" -ForegroundColor Yellow
                        return $false
                    }
                } else {
                    Write-Host "❌ Application Health : HTTP $($response.StatusCode)" -ForegroundColor Red
                    return $false
                }
            } catch {
                Write-Host "❌ Application Health : Connection failed" -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "❌ Cloud Run Service : $ServiceName not found" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Application Status : Check failed" -ForegroundColor Red
        return $false
    }
}

# Function to generate status summary
function New-StatusSummary {
    param($toolsOk, $authOk, $projectOk, $infraOk, $appOk)
    
    Write-Host "`n📊 Deployment Status Summary" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan
    
    $totalChecks = 5
    $passedChecks = 0
    
    if ($toolsOk) { $passedChecks++ }
    if ($authOk) { $passedChecks++ }
    if ($projectOk) { $passedChecks++ }
    if ($infraOk) { $passedChecks++ }
    if ($appOk) { $passedChecks++ }
    
    Write-Host "Tools Available: $(if ($toolsOk) { '✅' } else { '❌' })" -ForegroundColor $(if ($toolsOk) { 'Green' } else { 'Red' })
    Write-Host "Authentication: $(if ($authOk) { '✅' } else { '❌' })" -ForegroundColor $(if ($authOk) { 'Green' } else { 'Red' })
    Write-Host "Project Config: $(if ($projectOk) { '✅' } else { '❌' })" -ForegroundColor $(if ($projectOk) { 'Green' } else { 'Red' })
    Write-Host "Infrastructure: $(if ($infraOk) { '✅' } else { '❌' })" -ForegroundColor $(if ($infraOk) { 'Green' } else { 'Red' })
    Write-Host "Application: $(if ($appOk) { '✅' } else { '❌' })" -ForegroundColor $(if ($appOk) { 'Green' } else { 'Red' })
    
    Write-Host "`nOverall Status: $passedChecks/$totalChecks checks passed" -ForegroundColor Cyan
    
    if ($passedChecks -eq $totalChecks) {
        Write-Host "🎉 Deployment is fully operational!" -ForegroundColor Green
        return $true
    } elseif ($passedChecks -ge 3) {
        Write-Host "⚠️ Deployment is partially operational" -ForegroundColor Yellow
        return $false
    } else {
        Write-Host "❌ Deployment has significant issues" -ForegroundColor Red
        return $false
    }
}

# Function to provide next steps
function Show-NextSteps {
    param($toolsOk, $authOk, $projectOk, $infraOk, $appOk)
    
    Write-Host "`n📋 Recommended Next Steps" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    
    if (-not $toolsOk) {
        Write-Host "1. Install prerequisites: .\scripts\windows\Install-Prerequisites.ps1" -ForegroundColor White
    }
    
    if (-not $authOk) {
        Write-Host "2. Authenticate with GCP: gcloud auth login" -ForegroundColor White
    }
    
    if (-not $projectOk) {
        Write-Host "3. Set GCP project: gcloud config set project $ProjectId" -ForegroundColor White
    }
    
    if (-not $infraOk) {
        Write-Host "4. Setup infrastructure: .\scripts\windows\Setup-GCP-Infrastructure.ps1 -ProjectId $ProjectId" -ForegroundColor White
    }
    
    if (-not $appOk) {
        Write-Host "5. Deploy application: .\scripts\windows\Deploy-Production.ps1 -ProjectId $ProjectId" -ForegroundColor White
    }
    
    if ($toolsOk -and $authOk -and $projectOk -and $infraOk -and $appOk) {
        Write-Host "✅ All systems operational! No action required." -ForegroundColor Green
        Write-Host "🔗 Access your application at: $(gcloud run services describe $ServiceName --region=$Region --format='value(status.url)')" -ForegroundColor White
    }
}

# Main execution
try {
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Region: $Region" -ForegroundColor White
    Write-Host "Service: $ServiceName" -ForegroundColor White
    Write-Host ""
    
    # Check prerequisites
    Write-Host "🛠️ Prerequisites Check" -ForegroundColor Cyan
    Write-Host "---------------------" -ForegroundColor Cyan
    
    $toolsOk = $true
    $toolsOk = (Test-ToolAvailability "Google Cloud CLI" "gcloud version") -and $toolsOk
    $toolsOk = (Test-ToolAvailability "Terraform" "terraform version") -and $toolsOk
    $toolsOk = (Test-ToolAvailability "Python" "python --version") -and $toolsOk
    
    $authOk = Test-GCPAuthentication
    $projectOk = Test-ProjectConfiguration
    
    # Check infrastructure and application
    $infraOk = Test-InfrastructureStatus
    $appOk = Test-ApplicationStatus
    
    # Generate summary
    $deploymentHealthy = New-StatusSummary $toolsOk $authOk $projectOk $infraOk $appOk
    
    # Show next steps
    Show-NextSteps $toolsOk $authOk $projectOk $infraOk $appOk
    
    Write-Host ""
    if ($deploymentHealthy) {
        Write-Host "🎉 Your Validatus deployment is ready for production use!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "⚠️ Please address the issues above before proceeding." -ForegroundColor Yellow
        exit 1
    }
    
} catch {
    Write-Host "❌ Status check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
