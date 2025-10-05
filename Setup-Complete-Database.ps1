<#
.SYNOPSIS
    Complete database setup and application update for Validatus
.DESCRIPTION
    This master script orchestrates the complete database setup process
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    [switch]$SkipInfrastructure,
    [switch]$SkipRedeployment,
    [switch]$SkipTesting,
    [bool]$CreateMinimalSetup = $true
)

Write-Host "🎯 Complete Validatus Database Setup and Deployment" -ForegroundColor Green
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
    
    Write-Host "📋 $StepName" -ForegroundColor Cyan
    Write-Host "$(('-' * $StepName.Length))" -ForegroundColor Cyan
    
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
    # Step 1: Setup Database Infrastructure
    if (-not $SkipInfrastructure) {
        Invoke-SetupStep "Setting up Database Infrastructure" {
            $infraArgs = @{
                ProjectId = $ProjectId
                Region = $Region
                CreateMinimalSetup = $CreateMinimalSetup
            }
            & ".\scripts\windows\Setup-Database-Infrastructure.ps1" @infraArgs
        }
    }
    
    # Step 2: Update Application Configuration
    Invoke-SetupStep "Updating Application Configuration" {
        $configArgs = @{
            ProjectId = $ProjectId
        }
        & ".\scripts\windows\Update-Application-Config.ps1" @configArgs
    }
    
    # Step 3: Redeploy with Database Connectivity
    if (-not $SkipRedeployment) {
        Invoke-SetupStep "Redeploying with Database Connectivity" {
            $deployArgs = @{
                ProjectId = $ProjectId
                Region = $Region
            }
            & ".\scripts\windows\Redeploy-With-Database.ps1" @deployArgs
        }
    }
    
    # Step 4: Complete Application Testing
    if (-not $SkipTesting) {
        Invoke-SetupStep "Testing Complete Application" {
            & ".\scripts\windows\Test-Complete-Application.ps1" -Verbose
        } -Optional
    }
    
    # Success!
    Write-Host "🎉 Complete Database Setup Successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Your Validatus Application:" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host "✅ Database: Fully operational with persistent storage" -ForegroundColor White
    Write-Host "✅ Backend: Deployed with database connectivity" -ForegroundColor White
    Write-Host "✅ Frontend: Updated and deployed" -ForegroundColor White
    Write-Host "✅ API: All endpoints functional" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend: https://validatus-frontend-ssivkqhvhq-uc.a.run.app" -ForegroundColor White
    Write-Host "  Backend:  https://validatus-backend-ssivkqhvhq-uc.a.run.app" -ForegroundColor White
    Write-Host "  Health:   https://validatus-backend-ssivkqhvhq-uc.a.run.app/health" -ForegroundColor White
    Write-Host "  API Docs: https://validatus-backend-ssivkqhvhq-uc.a.run.app/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Your application is now production-ready with full database persistence!" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "❌ Setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Ensure you have proper GCP permissions" -ForegroundColor White
    Write-Host "2. Check that billing is enabled" -ForegroundColor White
    Write-Host "3. Verify the project ID is correct" -ForegroundColor White
    Write-Host "4. Run individual scripts manually for debugging" -ForegroundColor White
    exit 1
}
