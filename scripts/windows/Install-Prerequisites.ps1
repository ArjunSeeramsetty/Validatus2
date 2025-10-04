<#
.SYNOPSIS
    Install all prerequisites for Validatus deployment on Windows
.DESCRIPTION
    This script installs Google Cloud CLI, Terraform, Python, and other required tools
#>

[CmdletBinding()]
param(
    [switch]$SkipPython,
    [switch]$SkipGCloud,
    [switch]$SkipTerraform
)

Write-Host "🚀 Installing Validatus Prerequisites for Windows..." -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Function to check if running as Administrator
function Test-IsAdministrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check for Administrator privileges
if (-not (Test-IsAdministrator)) {
    Write-Host "❌ This script requires Administrator privileges." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

# Function to check if Chocolatey is installed
function Install-Chocolatey {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "📦 Installing Chocolatey..." -ForegroundColor Cyan
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "✅ Chocolatey installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✅ Chocolatey already installed" -ForegroundColor Green
    }
}

# Function to install Python
function Install-Python {
    if ($SkipPython) {
        Write-Host "⏭️ Skipping Python installation" -ForegroundColor Yellow
        return
    }

    Write-Host "🐍 Installing Python 3.11..." -ForegroundColor Cyan
    
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "3\.1[1-9]") {
            Write-Host "✅ Python 3.11+ already installed: $pythonVersion" -ForegroundColor Green
            return
        }
    }
    
    choco install python311 -y
    refreshenv
    
    # Verify installation
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $version = python --version
        Write-Host "✅ Python installed: $version" -ForegroundColor Green
    } else {
        Write-Host "❌ Python installation failed" -ForegroundColor Red
        exit 1
    }
}

# Function to install Google Cloud CLI
function Install-GoogleCloudCLI {
    if ($SkipGCloud) {
        Write-Host "⏭️ Skipping Google Cloud CLI installation" -ForegroundColor Yellow
        return
    }

    Write-Host "☁️ Installing Google Cloud CLI..." -ForegroundColor Cyan
    
    if (Get-Command gcloud -ErrorAction SilentlyContinue) {
        Write-Host "✅ Google Cloud CLI already installed" -ForegroundColor Green
        return
    }
    
    # Download and install Google Cloud CLI
    $installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
    $installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"
    
    Write-Host "📥 Downloading Google Cloud CLI installer..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    
    Write-Host "🔧 Running Google Cloud CLI installer..." -ForegroundColor Cyan
    Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
    
    # Add to PATH
    $gcpPath = "${env:LOCALAPPDATA}\Google\Cloud SDK\google-cloud-sdk\bin"
    if (Test-Path $gcpPath) {
        $env:PATH += ";$gcpPath"
        [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")
    }
    
    refreshenv
    
    # Verify installation
    if (Get-Command gcloud -ErrorAction SilentlyContinue) {
        Write-Host "✅ Google Cloud CLI installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Google Cloud CLI installation failed" -ForegroundColor Red
        exit 1
    }
}

# Function to install Terraform
function Install-Terraform {
    if ($SkipTerraform) {
        Write-Host "⏭️ Skipping Terraform installation" -ForegroundColor Yellow
        return
    }

    Write-Host "🏗️ Installing Terraform..." -ForegroundColor Cyan
    
    if (Get-Command terraform -ErrorAction SilentlyContinue) {
        Write-Host "✅ Terraform already installed" -ForegroundColor Green
        return
    }
    
    choco install terraform -y
    refreshenv
    
    # Verify installation
    if (Get-Command terraform -ErrorAction SilentlyContinue) {
        $version = terraform --version
        Write-Host "✅ Terraform installed: $version" -ForegroundColor Green
    } else {
        Write-Host "❌ Terraform installation failed" -ForegroundColor Red
        exit 1
    }
}

# Function to install additional tools
function Install-AdditionalTools {
    Write-Host "🔧 Installing additional tools..." -ForegroundColor Cyan
    
    # Install Git if not present
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "📦 Installing Git..." -ForegroundColor Cyan
        choco install git -y
    }
    
    # Install Docker Desktop
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "🐳 Installing Docker Desktop..." -ForegroundColor Cyan
        choco install docker-desktop -y
    }
    
    # Install curl
    if (-not (Get-Command curl -ErrorAction SilentlyContinue)) {
        Write-Host "📡 Installing curl..." -ForegroundColor Cyan
        choco install curl -y
    }
    
    refreshenv
    Write-Host "✅ Additional tools installed" -ForegroundColor Green
}

# Function to verify all installations
function Test-Prerequisites {
    Write-Host "🧪 Verifying installations..." -ForegroundColor Cyan
    
    $errors = @()
    
    # Check Python
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        $errors += "Python not found"
    }
    
    # Check Google Cloud CLI
    if (Get-Command gcloud -ErrorAction SilentlyContinue) {
        Write-Host "✅ Google Cloud CLI: Available" -ForegroundColor Green
    } else {
        $errors += "Google Cloud CLI not found"
    }
    
    # Check Terraform
    if (Get-Command terraform -ErrorAction SilentlyContinue) {
        $terraformVersion = terraform --version | Select-Object -First 1
        Write-Host "✅ Terraform: $terraformVersion" -ForegroundColor Green
    } else {
        $errors += "Terraform not found"
    }
    
    # Check Git
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "✅ Git: Available" -ForegroundColor Green
    } else {
        $errors += "Git not found"
    }
    
    if ($errors.Count -gt 0) {
        Write-Host "❌ Some prerequisites are missing:" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        return $false
    }
    
    Write-Host "✅ All prerequisites verified successfully!" -ForegroundColor Green
    return $true
}

# Main execution
try {
    Install-Chocolatey
    Install-Python
    Install-GoogleCloudCLI
    Install-Terraform
    Install-AdditionalTools
    
    if (Test-Prerequisites) {
        Write-Host ""
        Write-Host "🎉 Prerequisites installation completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Next steps:" -ForegroundColor Cyan
        Write-Host "1. Close and reopen PowerShell to refresh environment variables" -ForegroundColor White
        Write-Host "2. Run: gcloud auth login" -ForegroundColor White
        Write-Host "3. Run the Validatus setup script" -ForegroundColor White
    } else {
        Write-Host "❌ Prerequisites installation completed with errors" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error during installation: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
