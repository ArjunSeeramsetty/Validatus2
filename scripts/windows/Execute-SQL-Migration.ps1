#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Execute SQL migration on Cloud SQL database

.DESCRIPTION
    This script executes SQL migration files on the Cloud SQL PostgreSQL database
    to create the missing tables for Google Custom Search integration.

.PARAMETER ProjectId
    GCP Project ID (default: validatus-platform)

.PARAMETER Region
    GCP Region (default: us-central1)

.PARAMETER SqlFile
    Path to SQL file to execute (default: backend/migrations/002_create_url_collection_campaigns.sql)

.EXAMPLE
    .\Execute-SQL-Migration.ps1
    .\Execute-SQL-Migration.ps1 -SqlFile "backend/migrations/002_create_url_collection_campaigns.sql"
#>

param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1",
    [string]$SqlFile = "backend/migrations/002_create_url_collection_campaigns.sql"
)

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "🗄️ Executing SQL migration on Cloud SQL database..." -ForegroundColor Green
Write-Host "Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "SQL File: $SqlFile" -ForegroundColor Cyan

try {
    # Check if SQL file exists
    if (-not (Test-Path $SqlFile)) {
        Write-Host "❌ SQL file not found: $SqlFile" -ForegroundColor Red
        exit 1
    }
    
    # Read SQL content
    $sqlContent = Get-Content $SqlFile -Raw
    Write-Host "📄 SQL file loaded: $($sqlContent.Length) characters" -ForegroundColor Yellow
    
    # Execute SQL using gcloud sql query
    Write-Host "🚀 Executing SQL migration..." -ForegroundColor Yellow
    gcloud sql query --sql="$sqlContent" --project=$ProjectId --database=validatus validatus-sql
    
    Write-Host "✅ SQL migration executed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error executing SQL migration: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
