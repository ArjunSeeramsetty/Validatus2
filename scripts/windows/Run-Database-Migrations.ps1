#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run database migrations for Validatus platform

.DESCRIPTION
    This script runs Alembic database migrations to update the Cloud SQL database schema
    with the new tables for Google Custom Search integration.

.PARAMETER ProjectId
    GCP Project ID (default: validatus-platform)

.PARAMETER Region
    GCP Region (default: us-central1)

.EXAMPLE
    .\Run-Database-Migrations.ps1
    .\Run-Database-Migrations.ps1 -ProjectId "my-project" -Region "us-east1"
#>

param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1"
)

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "🗄️ Running database migrations for Validatus platform..." -ForegroundColor Green
Write-Host "Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan

try {
    # Change to backend directory
    Set-Location "backend"
    
    # Check if alembic.ini exists
    if (-not (Test-Path "alembic.ini")) {
        Write-Host "❌ alembic.ini not found in backend directory" -ForegroundColor Red
        exit 1
    }
    
    # Check current migration status
    Write-Host "📊 Checking current migration status..." -ForegroundColor Yellow
    alembic current
    
    # Show migration history
    Write-Host "📋 Available migrations:" -ForegroundColor Yellow
    alembic history --verbose
    
    # Run migrations
    Write-Host "🚀 Running database migrations..." -ForegroundColor Yellow
    alembic upgrade head
    
    # Check final migration status
    Write-Host "✅ Migration completed. Final status:" -ForegroundColor Green
    alembic current
    
    Write-Host "✅ Database migrations completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error running database migrations: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
} finally {
    # Return to original directory
    Set-Location ".."
}
