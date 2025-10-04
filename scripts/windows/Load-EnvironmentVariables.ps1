<#
.SYNOPSIS
    Safe environment variable loading utility for PowerShell
.DESCRIPTION
    This script provides safe methods to load environment variables from .env files
    with proper handling of special characters, quotes, and spaces.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EnvFile,
    
    [switch]$Robust
)

# Function to safely load environment variables
function Load-EnvironmentFile {
    param(
        [string]$FilePath
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Error "Environment file not found: $FilePath"
        return $false
    }
    
    Write-Host "📝 Loading environment variables from $FilePath..." -ForegroundColor Cyan
    
    $envContent = Get-Content $FilePath
    $loadedCount = 0
    
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
                $loadedCount++
            }
        }
    }
    
    Write-Host "✅ Loaded $loadedCount environment variables successfully" -ForegroundColor Green
    return $true
}

# Function to robustly load environment variables (alternative approach)
function Load-EnvironmentFileRobust {
    param(
        [string]$FilePath,
        [switch]$ProcessEscapes = $true
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Error "Environment file not found: $FilePath"
        return $false
    }
    
    Write-Host "📝 Loading environment variables from $FilePath (robust mode)..." -ForegroundColor Cyan
    
    $content = Get-Content $FilePath -Raw
    $loadedCount = 0
    
    # Split by lines and process each
    $lines = $content -split "`n"
    
    foreach ($line in $lines) {
        $line = $line.Trim()
        
        # Skip comments and empty lines
        if (-not $line -or $line.StartsWith("#")) {
            continue
        }
        
        # Find the first equals sign
        $equalsIndex = $line.IndexOf("=")
        if ($equalsIndex -le 0) {
            continue
        }
        
        $key = $line.Substring(0, $equalsIndex).Trim()
        $value = $line.Substring($equalsIndex + 1).Trim()
        
        # Handle various quote styles
        if ($value.Length -ge 2 -and $value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        } elseif ($value.Length -ge 2 -and $value.StartsWith("'") -and $value.EndsWith("'")) {
            $value = $value.Substring(1, $value.Length - 2)
        } elseif ($value.Length -ge 4 -and $value.StartsWith('`"') -and $value.EndsWith('`"')) {
            $value = $value.Substring(2, $value.Length - 4)
        }
        
        # Handle escaped characters in robust mode
        if ($ProcessEscapes) {
            $value = $value -replace '\\n', "`n"
            $value = $value -replace '\\r', "`r"
            $value = $value -replace '\\t', "`t"
            $value = $value -replace '\\"', '"'
            $value = $value -replace "\\'", "'"
            $value = $value -replace '\\\\', '\'
        }
        
        # Set environment variable
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
        $loadedCount++
        
        if ($Verbose) {
            Write-Host "  Set $key = $value" -ForegroundColor Gray
        }
    }
    
    Write-Host "✅ Loaded $loadedCount environment variables successfully (robust mode)" -ForegroundColor Green
    return $true
}

# Export functions for use in other scripts
Export-ModuleMember -Function Load-EnvironmentFile, Load-EnvironmentFileRobust

# Main execution
try {
    if ($Robust) {
        $success = Load-EnvironmentFileRobust -FilePath $EnvFile -ProcessEscapes
    } else {
        $success = Load-EnvironmentFile -FilePath $EnvFile
    }
    
    if ($success) {
        Write-Host "🎉 Environment variables loaded successfully!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Failed to load environment variables" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error loading environment variables: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
