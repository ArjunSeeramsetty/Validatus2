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
    # Skip comments and empty lines
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $equalsIndex = $line.IndexOf("=")
        if ($equalsIndex -gt 0) {
            $key = $line.Substring(0, $equalsIndex).Trim()
            $value = $line.Substring($equalsIndex + 1).Trim()
            
            # Handle quoted values
            if ($value.Length -ge 2 -and $value.StartsWith('"') -and $value.EndsWith('"')) {
                $value = $value.Substring(1, $value.Length - 2)
            } elseif ($value.Length -ge 2 -and $value.StartsWith("'") -and $value.EndsWith("'")) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            
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
