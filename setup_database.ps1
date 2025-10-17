# setup_database.ps1

# Database Setup Script for Results Persistence Tables
# This script runs the SQL migration via gcloud

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DATABASE SETUP FOR RESULTS PERSISTENCE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Configuration
$PROJECT_ID = "validatus-platform"
$INSTANCE_NAME = "validatus-db"
$DATABASE_NAME = "validatus"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project: $PROJECT_ID" -ForegroundColor White
Write-Host "  Instance: $INSTANCE_NAME" -ForegroundColor White
Write-Host "  Database: $DATABASE_NAME" -ForegroundColor White
Write-Host ""

# Check if gcloud is available
Write-Host "Checking gcloud CLI..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-String "Google Cloud SDK"
    Write-Host "  $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: gcloud CLI not found!" -ForegroundColor Red
    exit 1
}

Write-Host "`nRunning SQL migration..." -ForegroundColor Yellow
Write-Host "This will create 6 tables for results persistence:" -ForegroundColor White
Write-Host "  1. computed_factors" -ForegroundColor White
Write-Host "  2. pattern_matches" -ForegroundColor White
Write-Host "  3. monte_carlo_scenarios" -ForegroundColor White
Write-Host "  4. consumer_personas" -ForegroundColor White
Write-Host "  5. segment_rich_content" -ForegroundColor White
Write-Host "  6. results_generation_status" -ForegroundColor White
Write-Host ""

# Run the migration
Write-Host "Executing SQL migration..." -ForegroundColor Yellow
$result = gcloud sql connect $INSTANCE_NAME --user=postgres --database=$DATABASE_NAME --project=$PROJECT_ID --quiet 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nMigration completed successfully!" -ForegroundColor Green
    Write-Host "`nTo manually run the migration:" -ForegroundColor Yellow
    Write-Host "1. Copy contents of DIRECT_SQL_MIGRATION.sql" -ForegroundColor White
    Write-Host "2. Run: gcloud sql connect $INSTANCE_NAME --user=postgres --database=$DATABASE_NAME" -ForegroundColor White
    Write-Host "3. Paste the SQL and execute" -ForegroundColor White
} else {
    Write-Host "`nManual migration required." -ForegroundColor Yellow
    Write-Host "`nOption 1 - Via gcloud:" -ForegroundColor Cyan
    Write-Host "  gcloud sql connect $INSTANCE_NAME --user=postgres --database=$DATABASE_NAME --project=$PROJECT_ID" -ForegroundColor White
    Write-Host "  Then paste contents of DIRECT_SQL_MIGRATION.sql" -ForegroundColor White
    Write-Host "`nOption 2 - Via Google Cloud Console:" -ForegroundColor Cyan
    Write-Host "  1. Go to Cloud SQL in Google Cloud Console" -ForegroundColor White
    Write-Host "  2. Select $INSTANCE_NAME" -ForegroundColor White
    Write-Host "  3. Go to 'SQL' tab" -ForegroundColor White
    Write-Host "  4. Paste contents of DIRECT_SQL_MIGRATION.sql" -ForegroundColor White
    Write-Host "  5. Click 'Run'" -ForegroundColor White
}

Write-Host "`n========================================" -ForegroundColor Cyan
