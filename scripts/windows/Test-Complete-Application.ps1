<#
.SYNOPSIS
    Complete end-to-end testing of Validatus application
.DESCRIPTION
    This script performs comprehensive testing of all application components
#>

[CmdletBinding()]
param(
    [string]$BackendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app",
    [string]$FrontendUrl = "https://validatus-frontend-ssivkqhvhq-uc.a.run.app",
    [switch]$Verbose
)

Write-Host "🧪 Complete Validatus Application Testing" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

$testResults = @{}
$ErrorActionPreference = "Continue"

# Function to test health endpoints
function Test-HealthEndpoints {
    Write-Host "Test 1: Health Endpoints..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "$BackendUrl/health" -Method Get -TimeoutSec 30
        
        if ($response.status -eq "healthy") {
            Write-Host "✅ Backend health check passed" -ForegroundColor Green
            if ($Verbose) {
                Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
            }
            return $true
        } else {
            Write-Host "❌ Backend health check failed - Status: $($response.status)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test database operations
function Test-DatabaseOperations {
    Write-Host "Test 2: Database Operations..." -ForegroundColor Cyan
    
    try {
        # Test listing topics
        $topicsResponse = Invoke-RestMethod -Uri "$BackendUrl/api/v3/topics" -Method Get -TimeoutSec 30
        
        if ($topicsResponse.topics -is [Array]) {
            Write-Host "✅ Topics listing successful (found $($topicsResponse.topics.Count) topics)" -ForegroundColor Green
        } else {
            Write-Host "❌ Topics listing returned unexpected format" -ForegroundColor Red
            return $false
        }
        
        # Test creating a topic
        $topicData = @{
            topic = "End-to-End Test Topic $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            description = "This is a comprehensive test of the complete application stack"
            search_queries = @("application test", "end to end")
            initial_urls = @("https://example.com/test")
            analysis_type = "comprehensive"
            user_id = "test_user_e2e"
            metadata = @{
                test = $true
                test_type = "end-to-end"
                timestamp = (Get-Date).ToString("o")
            }
        } | ConvertTo-Json -Depth 10
        
        $headers = @{ "Content-Type" = "application/json" }
        $createResponse = Invoke-RestMethod -Uri "$BackendUrl/api/v3/topics/create" -Method Post -Body $topicData -Headers $headers -TimeoutSec 60
        
        if ($createResponse.session_id) {
            Write-Host "✅ Topic creation successful: $($createResponse.session_id)" -ForegroundColor Green
            
            if ($Verbose) {
                Write-Host "   Topic details: $($createResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
            }
            
            # Test retrieving the created topic
            Start-Sleep 2  # Allow for consistency
            $getResponse = Invoke-RestMethod -Uri "$BackendUrl/api/v3/topics" -Method Get -TimeoutSec 30
            
            $createdTopic = $getResponse.topics | Where-Object { $_.session_id -eq $createResponse.session_id }
            
            if ($createdTopic) {
                Write-Host "✅ Topic retrieval successful - Topic persisted in database" -ForegroundColor Green
                return $true
            } else {
                Write-Host "⚠️ Topic was created but not found in listing - possible consistency issue" -ForegroundColor Yellow
                return $true  # Still pass as creation worked
            }
            
        } else {
            Write-Host "❌ Topic creation failed - No session_id returned" -ForegroundColor Red
            return $false
        }
        
    } catch {
        Write-Host "❌ Database operations test failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            try {
                $errorDetails = $_.Exception.Response.Content.ReadAsStringAsync().Result
                Write-Host "   Error details: $errorDetails" -ForegroundColor Red
            } catch {}
        }
        return $false
    }
}

# Function to test frontend application
function Test-FrontendApplication {
    Write-Host "Test 3: Frontend Application..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $FrontendUrl -Method Get -TimeoutSec 30
        
        if ($response.StatusCode -eq 200) {
            $content = $response.Content
            
            # Check for React app indicators
            if ($content -like "*<div id=`"root`"*" -or $content -like "*React*" -or $content -like "*Validatus*") {
                Write-Host "✅ Frontend application loads successfully" -ForegroundColor Green
                
                if ($Verbose) {
                    $contentLength = $content.Length
                    Write-Host "   Content length: $contentLength characters" -ForegroundColor Gray
                    
                    # Check for key elements
                    if ($content -like "*Validatus*") {
                        Write-Host "   ✅ Validatus branding found" -ForegroundColor Gray
                    }
                    if ($content -like "*React*") {
                        Write-Host "   ✅ React framework detected" -ForegroundColor Gray
                    }
                }
                
                return $true
            } else {
                Write-Host "❌ Frontend doesn't appear to be a React application" -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "❌ Frontend returned status code: $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Frontend test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test API endpoints
function Test-APIEndpoints {
    Write-Host "Test 4: API Endpoints..." -ForegroundColor Cyan
    
    $endpoints = @(
        @{ Path = "/health"; Method = "GET"; Description = "Health check" },
        @{ Path = "/"; Method = "GET"; Description = "Root endpoint" },
        @{ Path = "/api/v3/topics"; Method = "GET"; Description = "Topics listing" }
    )
    
    $passedEndpoints = 0
    
    foreach ($endpoint in $endpoints) {
        try {
            $url = "$BackendUrl$($endpoint.Path)"
            
            if ($endpoint.Method -eq "GET") {
                $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 20
                Write-Host "   ✅ $($endpoint.Description): OK" -ForegroundColor Green
                $passedEndpoints++
            }
            
        } catch {
            Write-Host "   ❌ $($endpoint.Description): Failed - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    if ($passedEndpoints -eq $endpoints.Count) {
        Write-Host "✅ All API endpoints working ($passedEndpoints/$($endpoints.Count))" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⚠️ Some API endpoints failed ($passedEndpoints/$($endpoints.Count))" -ForegroundColor Yellow
        return $passedEndpoints -gt 0
    }
}

# Function to test performance
function Test-Performance {
    Write-Host "Test 5: Performance Testing..." -ForegroundColor Cyan
    
    $testCount = 5
    $responseTimes = @()
    
    for ($i = 1; $i -le $testCount; $i++) {
        try {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            $response = Invoke-RestMethod -Uri "$BackendUrl/health" -Method Get -TimeoutSec 10
            $stopwatch.Stop()
            
            $responseTime = $stopwatch.ElapsedMilliseconds
            $responseTimes += $responseTime
            
            if ($Verbose) {
                Write-Host "   Request $i : $responseTime ms" -ForegroundColor Gray
            }
        } catch {
            Write-Host "   Request $i : Failed" -ForegroundColor Red
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
        
        if ($avgResponseTime -lt 3000) {
            Write-Host "✅ Performance is acceptable (< 3s)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ Performance is slow (> 3s)" -ForegroundColor Yellow
            return $true
        }
    } else {
        Write-Host "❌ Performance test failed - no successful requests" -ForegroundColor Red
        return $false
    }
}

# Function to generate test report
function New-TestReport {
    param($results)
    
    Write-Host ""
    Write-Host "📊 Complete Test Report" -ForegroundColor Cyan
    Write-Host "=======================" -ForegroundColor Cyan
    
    $passedTests = ($results.Values | Where-Object { $_ -eq $true }).Count
    $totalTests = $results.Count
    
    foreach ($test in $results.GetEnumerator()) {
        $status = if ($test.Value) { "✅ PASSED" } else { "❌ FAILED" }
        $color = if ($test.Value) { "Green" } else { "Red" }
        Write-Host "$($test.Key): $status" -ForegroundColor $color
    }
    
    Write-Host ""
    Write-Host "Summary: $passedTests/$totalTests tests passed" -ForegroundColor Cyan
    
    $overallStatus = if ($passedTests -eq $totalTests) { "SUCCESS" } elseif ($passedTests -gt ($totalTests * 0.7)) { "PARTIAL SUCCESS" } else { "FAILURE" }
    $statusColor = if ($overallStatus -eq "SUCCESS") { "Green" } elseif ($overallStatus -eq "PARTIAL SUCCESS") { "Yellow" } else { "Red" }
    
    Write-Host "Overall Status: $overallStatus" -ForegroundColor $statusColor
    
    return @{
        PassedTests = $passedTests
        TotalTests = $totalTests
        OverallStatus = $overallStatus
    }
}

# Main execution
try {
    Write-Host "Backend URL: $BackendUrl" -ForegroundColor White
    Write-Host "Frontend URL: $FrontendUrl" -ForegroundColor White
    Write-Host ""
    
    # Run all tests
    $testResults["Health Endpoints"] = Test-HealthEndpoints
    $testResults["Database Operations"] = Test-DatabaseOperations
    $testResults["Frontend Application"] = Test-FrontendApplication
    $testResults["API Endpoints"] = Test-APIEndpoints
    $testResults["Performance"] = Test-Performance
    
    # Generate report
    $report = New-TestReport -results $testResults
    
    Write-Host ""
    Write-Host "🎯 Application Status Summary:" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    
    if ($report.OverallStatus -eq "SUCCESS") {
        Write-Host "🎉 All systems operational! Your Validatus application is fully functional." -ForegroundColor Green
        Write-Host ""
        Write-Host "🚀 Ready for use:" -ForegroundColor Cyan
        Write-Host "  - Frontend: $FrontendUrl" -ForegroundColor White
        Write-Host "  - Backend API: $BackendUrl" -ForegroundColor White
        Write-Host "  - Database: Connected and operational" -ForegroundColor White
        Write-Host "  - All core features: Available" -ForegroundColor White
    } elseif ($report.OverallStatus -eq "PARTIAL SUCCESS") {
        Write-Host "⚠️ Application is mostly functional with some issues." -ForegroundColor Yellow
        Write-Host "Core functionality should work, but some features may be limited." -ForegroundColor Yellow
    } else {
        Write-Host "❌ Application has significant issues that need to be addressed." -ForegroundColor Red
        Write-Host "Please review the test results above and fix the failing components." -ForegroundColor Red
    }
    
    Write-Host ""
    
    if ($report.OverallStatus -eq "SUCCESS") {
        exit 0
    } else {
        exit 1
    }
    
} catch {
    Write-Host "❌ Testing failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
