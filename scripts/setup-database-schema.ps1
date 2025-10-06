# PowerShell script to set up database schema
param(
    [string]$ProjectId = "validatus-platform",
    [string]$InstanceId = "validatus-sql",
    [string]$DatabaseName = "validatusdb"
)

Write-Host "Setting up database schema for Cloud SQL instance..." -ForegroundColor Green

# Get the instance connection name
$connectionName = "${ProjectId}:us-central1-c:${InstanceId}"
Write-Host "Connection name: $connectionName"

# Read the schema file
$schemaFile = "backend/migrations/001_initial_schema.sql"
if (-not (Test-Path $schemaFile)) {
    Write-Error "Schema file not found: $schemaFile"
    exit 1
}

$schemaContent = Get-Content $schemaFile -Raw
Write-Host "Schema file loaded: $schemaFile"

# Create a temporary file for the schema
$tempSchemaFile = [System.IO.Path]::GetTempFileName() + ".sql"
$schemaContent | Out-File -FilePath $tempSchemaFile -Encoding UTF8

try {
    # Execute the schema using gcloud sql execute-sql
    Write-Host "Executing database schema..." -ForegroundColor Yellow
    
    $result = gcloud sql execute-sql $InstanceId --database=$DatabaseName --file=$tempSchemaFile --project=$ProjectId 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database schema setup completed successfully!" -ForegroundColor Green
        Write-Host $result
    } else {
        Write-Host "❌ Database schema setup failed!" -ForegroundColor Red
        Write-Host $result
        exit 1
    }
} finally {
    # Clean up temporary file
    if (Test-Path $tempSchemaFile) {
        Remove-Item $tempSchemaFile -Force
    }
}

Write-Host "Database schema setup complete!" -ForegroundColor Green
