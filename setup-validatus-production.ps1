<#
.SYNOPSIS
    One-command setup for Validatus production deployment on Windows
.DESCRIPTION
    This script orchestrates the complete setup process for Validatus on GCP
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    [switch]$SkipPrerequisites,
    [switch]$SkipInfrastructure, 
    [switch]$SkipDeployment,
    [switch]$AutoApprove
)

Write-Host "🚀 Validatus Production Setup - One Command Deploy" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host "Project ID: $ProjectId" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host ""

$ErrorActionPreference = "Stop"

# Function to run step with error handling
function Invoke-SetupStep {
    param(
        [string]$StepName,
        [scriptblock]$ScriptBlock,
        [switch]$Optional
    )
    
    Write-Host "📋 Step: $StepName" -ForegroundColor Cyan
    Write-Host "$(('-' * $StepName.Length))------" -ForegroundColor Cyan
    
    try {
        & $ScriptBlock
        Write-Host "✅ $StepName completed successfully!" -ForegroundColor Green
        Write-Host ""
        return $true
    } catch {
        if ($Optional) {
            Write-Host "⚠️ $StepName failed but continuing: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host ""
            return $false
        } else {
            Write-Host "❌ $StepName failed: $($_.Exception.Message)" -ForegroundColor Red
            throw
        }
    }
}

try {
    # Step 1: Install Prerequisites
    if (-not $SkipPrerequisites) {
        Invoke-SetupStep "Installing Prerequisites" {
            if (Test-Path "scripts\windows\Install-Prerequisites.ps1") {
                & ".\scripts\windows\Install-Prerequisites.ps1"
            } else {
                Write-Host "⚠️ Prerequisites script not found, assuming tools are installed" -ForegroundColor Yellow
            }
        } -Optional
    }
    
    # Step 2: Setup GCP Infrastructure
    if (-not $SkipInfrastructure) {
        Invoke-SetupStep "Setting up GCP Infrastructure" {
            if (Test-Path "scripts\windows\Setup-GCP-Infrastructure.ps1") {
                $infraArgs = @{
                    ProjectId = $ProjectId
                    Region = $Region
                }
                if ($AutoApprove) {
                    $infraArgs.AutoApprove = $true
                }
                & ".\scripts\windows\Setup-GCP-Infrastructure.ps1" @infraArgs
            } else {
                Write-Host "❌ Infrastructure setup script not found" -ForegroundColor Red
                throw "Missing Setup-GCP-Infrastructure.ps1"
            }
        }
    }
    
    # Step 3: Deploy Application
    if (-not $SkipDeployment) {
        Invoke-SetupStep "Deploying Application" {
            if (Test-Path "scripts\windows\Deploy-Production.ps1") {
                & ".\scripts\windows\Deploy-Production.ps1" -ProjectId $ProjectId -Region $Region
            } else {
                Write-Host "❌ Deployment script not found" -ForegroundColor Red
                throw "Missing Deploy-Production.ps1"
            }
        }
    }
    
    # Step 4: Verify Deployment
    Invoke-SetupStep "Verifying Deployment" {
        if (Test-Path "scripts\windows\Verify-Production.ps1") {
            & ".\scripts\windows\Verify-Production.ps1" -ProjectId $ProjectId -Region $Region
        } else {
            Write-Host "⚠️ Verification script not found, skipping verification" -ForegroundColor Yellow
        }
    } -Optional
    
    # Success!
    Write-Host "🎉 Validatus production setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    
    $serviceUrl = gcloud run services describe validatus-backend --region=$Region --format="value(status.url)" 2>$null
    
    if ($serviceUrl) {
        Write-Host "🎯 Your Validatus Application:" -ForegroundColor Cyan
        Write-Host "=============================" -ForegroundColor Cyan
        Write-Host "🌐 Application URL: $serviceUrl" -ForegroundColor White
        Write-Host "📋 Health Check: $serviceUrl/health" -ForegroundColor White
        Write-Host "📖 API Documentation: $serviceUrl/docs" -ForegroundColor White
        Write-Host "🔧 GCP Console: https://console.cloud.google.com/run?project=$ProjectId" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "🚀 Your application is now running on GCP with full database persistence!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Test your application thoroughly" -ForegroundColor White
    Write-Host "2. Configure custom domain (optional)" -ForegroundColor White
    Write-Host "3. Set up monitoring alerts" -ForegroundColor White
    Write-Host "4. Configure backup and disaster recovery" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "❌ Setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check that you have the required permissions in GCP" -ForegroundColor White
    Write-Host "2. Ensure billing is enabled for your GCP project" -ForegroundColor White
    Write-Host "3. Verify all prerequisites are installed" -ForegroundColor White
    Write-Host "4. Check the error details above" -ForegroundColor White
    Write-Host ""
    exit 1
}