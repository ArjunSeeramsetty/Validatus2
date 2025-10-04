<#
.SYNOPSIS
    Set environment variables for local development on Windows
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EnvFile = ".env.production"
)

if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Environment file not found: $EnvFile" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Setting environment variables from $EnvFile..." -ForegroundColor Cyan

$envContent = Get-Content $EnvFile

foreach ($line in $envContent) {
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $parts = $line.Split("=", 2)
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            
            # Set for current session
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
            
            # Set for user (persistent)
            [Environment]::SetEnvironmentVariable($key, $value, "User")
            
            Write-Host "✅ Set $key" -ForegroundColor Green
        }
    }
}

Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green
Write-Host "Please restart PowerShell for changes to take effect." -ForegroundColor Yellow
