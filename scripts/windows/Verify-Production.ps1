<#
.SYNOPSIS
    Verify Validatus production deployment
.DESCRIPTION
    This script runs comprehensive tests to verify the production deployment
#>

[CmdletBinding()]
param(
    [string]$ProjectId = "validatus-platform",
    [string]$Region = "us-central1", 
    [string]$ServiceName = "validatus-backend",
    [string]$BaseUrl = "",
    [switch]$SkipApiTests,
    [switch]$Verbose
)

Write-Host "🧪 Verifying Validatus Production Deployment" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Get service URL if not provided
if (-not $BaseUrl) {
    Write-Host "🔍 Getting service URL..." -ForegroundColor Cyan
    $BaseUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"
    
    if (-not $BaseUrl) {
        Write-Host "❌ Failed to get service URL" -ForegroundColor Red
        exit 1
    }
}

Write-Host "🌐 Testing URL: $BaseUrl" -ForegroundColor White
Write-Host ""

# Function to test health endpoint
function Test-HealthEndpoint {
    Write-Host "Test 1: Health check..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 30
        
        if ($response.status -eq "healthy") {
            Write-Host "✅ Health check passed: $($response.status)" -ForegroundColor Green
            
            if ($Verbose -and $response.gcp_services) {
                Write-Host "   GCP Services Status:" -ForegroundColor Gray
                foreach ($service in $response.gcp_services.services.PSObject.Properties) {
                    $serviceName = $service.Name
                    $serviceStatus = $service.Value.status
                    
                    if ($serviceStatus -eq "healthy") {
                        Write-Host "     ✅ $serviceName" -ForegroundColor Green
                    } else {
                        Write-Host "     ❌ $serviceName: $serviceStatus" -ForegroundColor Red
                    }
                }
            }
            
            return $true
        } else {
            Write-Host "❌ Health check failed: $($response.status)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test topic creation
function Test-TopicCreation {
    if ($SkipApiTests) {
        Write-Host "⏭️ Skipping API tests" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "Test 2: Creating test topic..." -ForegroundColor Cyan
    
    $topicData = @{
        topic = "Production Test Topic $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        description = "Testing production deployment from PowerShell"
        search_queries = @("production test", "powershell deployment")
        initial_urls = @("https://example.com/test")
        analysis_type = "comprehensive"
        user_id = "test_user_production_ps"
        metadata = @{
            test = $true
            timestamp = (Get-Date).ToString("o")
            client = "PowerShell"
        }
    } | ConvertTo-Json -Depth 10
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v3/topics/create" -Method Post -Body $topicData -Headers $headers -TimeoutSec 60
        
        if ($response.session_id) {
            Write-Host "✅ Topic created successfully: $($response.session_id)" -ForegroundColor Green
            
            # Test topic retrieval
            Write-Host "Test 3: Retrieving created topic..." -ForegroundColor Cyan
            
            try {
                $getResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/topics" -Method Get -TimeoutSec 30
                
                if ($getResponse.topics -and $getResponse.topics.Count -gt 0) {
                    Write-Host "✅ Topic retrieval successful (found $($getResponse.topics.Count) topics)" -ForegroundColor Green
                    return $true
                } else {
                    Write-Host "⚠️ Topic retrieval returned no topics" -ForegroundColor Yellow
                    return $true
                }
            } catch {
                Write-Host "❌ Topic retrieval failed: $($_.Exception.Message)" -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "❌ Topic creation failed: No session_id returned" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Topic creation failed: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode
            Write-Host "   Status Code: $statusCode" -ForegroundColor Red
            
            try {
                $errorContent = $_.Exception.Response.Content.ReadAsStringAsync().Result
                Write-Host "   Error Details: $errorContent" -ForegroundColor Red
            } catch {
                # Ignore error reading content
            }
        }
        
        return $false
    }
}

# Function to test database connectivity
function Test-DatabaseConnectivity {
    Write-Host "Test 4: Database connectivity..." -ForegroundColor Cyan
    
    try {
        # Test through health endpoint with detailed info
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 30
        
        if ($response.gcp_services -and $response.gcp_services.services) {
            $services = $response.gcp_services.services
            
            # Check SQL service
            if ($services.sql -and $services.sql.status -eq "healthy") {
                Write-Host "✅ Cloud SQL connection successful" -ForegroundColor Green
            } else {
                Write-Host "❌ Cloud SQL connection failed" -ForegroundColor Red
                return $false
            }
            
            # Check Redis service
            if ($services.redis -and $services.redis.status -eq "healthy") {
                Write-Host "✅ Redis connection successful" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Redis connection issues detected" -ForegroundColor Yellow
            }
            
            # Check Storage service
            if ($services.storage -and $services.storage.status -eq "healthy") {
                Write-Host "✅ Cloud Storage connection successful" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Cloud Storage connection issues detected" -ForegroundColor Yellow
            }
            
            return $true
        } else {
            Write-Host "⚠️ GCP services status not available in health check" -ForegroundColor Yellow
            return $true
        }
    } catch {
        Write-Host "❌ Database connectivity test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test performance
function Test-Performance {
    Write-Host "Test 5: Performance check..." -ForegroundColor Cyan
    
    $testCount = 5
    $responseTimes = @()
    
    for ($i = 1; $i -le $testCount; $i++) {
        try {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 10
            $stopwatch.Stop()
            
            $responseTime = $stopwatch.ElapsedMilliseconds
            $responseTimes += $responseTime
            
            Write-Host "  Request $i : $responseTime ms" -ForegroundColor Gray
        } catch {
            Write-Host "  Request $i : Failed" -ForegroundColor Red
        }
    }
    
    if ($responseTimes.Count -gt 0) {
        $avgResponseTime = ($responseTimes | Measure-Object -Average).Average
        $minResponseTime = ($responseTimes | Measure-Object -Minimum).Minimum
        $maxResponseTime = ($responseTimes | Measure-Object -Maximum).Maximum
        
        Write-Host "✅ Performance results:" -ForegroundColor Green
        Write-Host "   Average: $([Math]::Round($avgResponseTime, 2)) ms" -ForegroundColor White
        Write-Host "   Min: $minResponseTime ms" -ForegroundColor White
        Write-Host "   Max: $maxResponseTime ms" -ForegroundColor White
        
        if ($avgResponseTime -lt 2000) {
            Write-Host "✅ Performance is good (< 2s)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ Performance is slow (> 2s)" -ForegroundColor Yellow
            return $true
        }
    } else {
        Write-Host "❌ Performance test failed - no successful requests" -ForegroundColor Red
        return $false
    }
}

# Function to generate verification report
function New-VerificationReport {
    param($results)
    
    Write-Host ""
    Write-Host "📊 Verification Report" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    
    $passedTests = ($results.Values | Where-Object { $_ -eq $true }).Count
    $totalTests = $results.Count
    
    foreach ($test in $results.GetEnumerator()) {
        $status = if ($test.Value) { "✅ PASSED" } else { "❌ FAILED" }
        $color = if ($test.Value) { "Green" } else { "Red" }
        Write-Host "$($test.Key): $status" -ForegroundColor $color
    }
    
    Write-Host ""
    Write-Host "Summary: $passedTests/$totalTests tests passed" -ForegroundColor Cyan
    
    if ($passedTests -eq $totalTests) {
        Write-Host "🎉 All verification tests passed!" -ForegroundColor Green
        Write-Host "Your Validatus application is running successfully!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⚠️ Some verification tests failed" -ForegroundColor Yellow
        Write-Host "Please review the results above" -ForegroundColor Yellow
        return $false
    }
}

# Main execution
try {
    $results = @{}
    
    # Run all tests
    $results["Health Check"] = Test-HealthEndpoint
    $results["Database Connectivity"] = Test-DatabaseConnectivity
    $results["Topic Creation"] = Test-TopicCreation
    $results["Performance Check"] = Test-Performance
    
    # Generate report
    $allTestsPassed = New-VerificationReport -results $results
    
    Write-Host ""
    Write-Host "🎯 Production Environment Details:" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "🌐 Application URL: $BaseUrl" -ForegroundColor White
    Write-Host "📋 Health Endpoint: $BaseUrl/health" -ForegroundColor White
    Write-Host "📖 API Documentation: $BaseUrl/docs" -ForegroundColor White
    Write-Host "🔧 GCP Console: https://console.cloud.google.com/run/detail/$Region/$ServiceName/metrics?project=$ProjectId" -ForegroundColor White
    Write-Host ""
    
    if ($allTestsPassed) {
        exit 0
    } else {
        exit 1
    }
    
} catch {
    Write-Host "❌ Verification failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}
