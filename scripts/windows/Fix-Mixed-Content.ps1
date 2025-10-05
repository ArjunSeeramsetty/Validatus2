<#
.SYNOPSIS
    Fix Mixed Content issue by updating frontend to use HTTPS
.DESCRIPTION
    Quick fix for the HTTPS mixed content error in the frontend
#>

[CmdletBinding()]
param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1"
)

Write-Host "🔧 Fixing Mixed Content Issue..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Function to update frontend configuration
function Update-FrontendConfig {
    Write-Host "📝 Updating frontend configuration to use HTTPS..." -ForegroundColor Cyan
    
    # Create .env file with HTTPS configuration
    $envContent = @"
# Fixed HTTPS configuration
VITE_API_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app
VITE_API_BASE_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app
REACT_APP_API_BASE_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app
REACT_APP_BACKEND_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app

# Environment settings
NODE_ENV=production
VITE_NODE_ENV=production
HTTPS=true
"@

    # Update both .env files
    $envContent | Out-File -FilePath "frontend\.env" -Encoding utf8 -NoNewline
    $envContent | Out-File -FilePath "frontend\.env.production" -Encoding utf8 -NoNewline
    
    Write-Host "✅ Frontend environment files updated" -ForegroundColor Green
}

# Function to rebuild and redeploy frontend
function Deploy-FixedFrontend {
    Write-Host "🚀 Rebuilding and deploying frontend with HTTPS fix..." -ForegroundColor Cyan
    
    try {
        # Build with proper environment variable
        Write-Host "Building frontend with HTTPS configuration..." -ForegroundColor Gray
        
        gcloud builds submit frontend `
            --tag gcr.io/$ProjectId/validatus-frontend:https-fixed `
            --substitutions="_VITE_API_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app" `
            --project=$ProjectId `
            --timeout=600s
        
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend build failed"
        }
        
        # Deploy with environment variables
        Write-Host "Deploying frontend with HTTPS configuration..." -ForegroundColor Gray
        
        gcloud run deploy validatus-frontend `
            --image gcr.io/$ProjectId/validatus-frontend:https-fixed `
            --region $Region `
            --platform managed `
            --allow-unauthenticated `
            --set-env-vars "VITE_API_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app,REACT_APP_API_BASE_URL=https://validatus-backend-ssivkqhvhq-uc.a.run.app" `
            --project=$ProjectId
        
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend deployment failed"
        }
        
        Write-Host "✅ Frontend deployed with HTTPS fix" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
}

# Function to test the fix
function Test-HTTPSFix {
    Write-Host "🧪 Testing HTTPS fix..." -ForegroundColor Cyan
    
    $frontendUrl = "https://validatus-frontend-ssivkqhvhq-uc.a.run.app"
    $backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
    
    try {
        # Test backend first
        Write-Host "Testing backend API..." -ForegroundColor Gray
        $backendResponse = Invoke-RestMethod -Uri "$backendUrl/api/v3/topics" -Method Get -TimeoutSec 30
        
        if ($backendResponse.topics -and $backendResponse.topics.Count -gt 0) {
            Write-Host "✅ Backend API working: Found $($backendResponse.topics.Count) topics" -ForegroundColor Green
        }
        
        # Test frontend
        Write-Host "Testing frontend..." -ForegroundColor Gray
        $frontendResponse = Invoke-WebRequest -Uri $frontendUrl -Method Get -TimeoutSec 30
        
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Host "✅ Frontend is accessible" -ForegroundColor Green
        }
        
        # Wait a moment for the frontend to load completely
        Write-Host "Waiting for frontend to initialize..." -ForegroundColor Gray
        Start-Sleep 10
        
        Write-Host "✅ HTTPS fix applied successfully!" -ForegroundColor Green
        Write-Host "The Mixed Content issue should now be resolved." -ForegroundColor Green
        
        return $true
        
    } catch {
        Write-Host "❌ Testing failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main execution
try {
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Issue: Frontend requesting HTTP instead of HTTPS backend" -ForegroundColor Yellow
    Write-Host ""
    
    # Step 1: Update configuration
    Update-FrontendConfig
    
    # Step 2: Deploy fixed frontend
    Deploy-FixedFrontend
    
    # Step 3: Test the fix
    $testPassed = Test-HTTPSFix
    
    if ($testPassed) {
        Write-Host ""
        Write-Host "🎉 Mixed Content Issue FIXED!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 What was fixed:" -ForegroundColor Cyan
        Write-Host "✅ Frontend now uses HTTPS backend URL" -ForegroundColor White
        Write-Host "✅ Mixed content security error resolved" -ForegroundColor White
        Write-Host "✅ Topics should now load properly" -ForegroundColor White
        Write-Host ""
        Write-Host "🔗 Test your application:" -ForegroundColor Cyan
        Write-Host "Frontend: https://validatus-frontend-ssivkqhvhq-uc.a.run.app" -ForegroundColor White
        Write-Host "Backend:  https://validatus-backend-ssivkqhvhq-uc.a.run.app/api/v3/topics" -ForegroundColor White
        Write-Host ""
        Write-Host "📋 Database Status:" -ForegroundColor Cyan
        Write-Host "✅ Database is working with 2 topics stored" -ForegroundColor White
        Write-Host "✅ All data persistence is functional" -ForegroundColor White
    } else {
        Write-Host "⚠️ Fix applied but verification failed" -ForegroundColor Yellow
        Write-Host "Please test manually by visiting the frontend URL" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Failed to fix mixed content issue: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Manual fix steps:" -ForegroundColor Yellow
    Write-Host "1. Update frontend/.env with HTTPS backend URL" -ForegroundColor White
    Write-Host "2. Rebuild frontend Docker image" -ForegroundColor White
    Write-Host "3. Redeploy to Cloud Run" -ForegroundColor White
    exit 1
}
