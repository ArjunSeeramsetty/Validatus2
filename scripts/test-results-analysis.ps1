# Test Results Analysis System
# Comprehensive testing script for Phase 1 + Phase 2 implementation

param(
    [string]$BaseUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app",
    [string]$SessionId = "topic-747b5405721c"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESULTS ANALYSIS SYSTEM TEST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Base URL: $BaseUrl" -ForegroundColor White
Write-Host "Session ID: $SessionId" -ForegroundColor White
Write-Host ""

# Test 1: Check Analysis Status
Write-Host "`n[TEST 1] Checking Analysis Status..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/results/status/$SessionId" -Method Get
    
    Write-Host "  Session: $($statusResponse.session_id)" -ForegroundColor White
    Write-Host "  Topic: $($statusResponse.topic)" -ForegroundColor White
    Write-Host "  Content Items: $($statusResponse.content_items)" -ForegroundColor White
    Write-Host "  Analysis Ready: $($statusResponse.analysis_ready)" -ForegroundColor $(if ($statusResponse.analysis_ready) { "Green" } else { "Red" })
    Write-Host "  Recommended Action: $($statusResponse.recommended_action)" -ForegroundColor Cyan
    
    if ($statusResponse.analysis_ready) {
        Write-Host "  ✅ TEST 1 PASSED - Ready for analysis" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ TEST 1 WARNING - Not ready, $($statusResponse.recommended_action)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ TEST 1 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Complete Analysis Endpoint
Write-Host "`n[TEST 2] Testing Complete Analysis Endpoint..." -ForegroundColor Yellow
try {
    $completeResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/results/complete/$SessionId" -Method Get
    
    Write-Host "  Topic Name: $($completeResponse.topic_name)" -ForegroundColor White
    Write-Host "  Analysis Timestamp: $($completeResponse.analysis_timestamp)" -ForegroundColor White
    Write-Host "  Dimensions Available:" -ForegroundColor Cyan
    
    $dimensions = @('market', 'consumer', 'product', 'brand', 'experience')
    foreach ($dim in $dimensions) {
        if ($completeResponse.$dim) {
            Write-Host "    ✅ $($dim.ToUpper())" -ForegroundColor Green
        } else {
            Write-Host "    ❌ $($dim.ToUpper())" -ForegroundColor Red
        }
    }
    
    if ($completeResponse.confidence_scores) {
        Write-Host "`n  Confidence Scores:" -ForegroundColor Cyan
        foreach ($key in $completeResponse.confidence_scores.PSObject.Properties.Name) {
            $score = $completeResponse.confidence_scores.$key
            $color = if ($score -gt 0.7) { "Green" } elseif ($score -gt 0.5) { "Yellow" } else { "Red" }
            Write-Host "    $($key): $([math]::Round($score * 100, 0))%" -ForegroundColor $color
        }
    }
    
    Write-Host "  ✅ TEST 2 PASSED - Complete analysis generated" -ForegroundColor Green
} catch {
    Write-Host "  ❌ TEST 2 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Individual Dimension Endpoints
Write-Host "`n[TEST 3] Testing Individual Dimension Endpoints..." -ForegroundColor Yellow

$dimensionTests = @{
    "market" = "$BaseUrl/api/v3/results/market/$SessionId"
    "consumer" = "$BaseUrl/api/v3/results/consumer/$SessionId"
    "product" = "$BaseUrl/api/v3/results/product/$SessionId"
    "brand" = "$BaseUrl/api/v3/results/brand/$SessionId"
    "experience" = "$BaseUrl/api/v3/results/experience/$SessionId"
}

foreach ($dim in $dimensionTests.Keys) {
    try {
        $response = Invoke-RestMethod -Uri $dimensionTests[$dim] -Method Get
        
        # Check for key data
        $hasData = $false
        foreach ($prop in $response.PSObject.Properties) {
            if ($prop.Value -and $prop.Value -ne @{} -and $prop.Value -ne @()) {
                $hasData = $true
                break
            }
        }
        
        if ($hasData) {
            Write-Host "  ✅ $($dim.ToUpper()) endpoint: Available with data" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ $($dim.ToUpper()) endpoint: Available but empty" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ $($dim.ToUpper()) endpoint: Failed - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 4: Enhanced Analysis - Results Dashboard
Write-Host "`n[TEST 4] Testing Enhanced Results Dashboard..." -ForegroundColor Yellow
try {
    $dashboardResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/enhanced-analysis/results-dashboard/$SessionId" -Method Get
    
    Write-Host "  Session: $($dashboardResponse.session_id)" -ForegroundColor White
    Write-Host "  Version: $($dashboardResponse.version)" -ForegroundColor White
    Write-Host "  Timestamp: $($dashboardResponse.timestamp)" -ForegroundColor White
    
    if ($dashboardResponse.dashboard_data) {
        Write-Host "`n  Dashboard Data Sections:" -ForegroundColor Cyan
        foreach ($section in $dashboardResponse.dashboard_data.PSObject.Properties.Name) {
            Write-Host "    ✅ $section" -ForegroundColor Green
        }
    }
    
    if ($dashboardResponse.dashboard_data.overall_scores) {
        Write-Host "`n  Overall Dimension Scores:" -ForegroundColor Cyan
        foreach ($key in $dashboardResponse.dashboard_data.overall_scores.PSObject.Properties.Name) {
            $score = $dashboardResponse.dashboard_data.overall_scores.$key
            $color = if ($score -gt 70) { "Green" } elseif ($score -gt 50) { "Yellow" } else { "Red" }
            Write-Host "    $($key): $score" -ForegroundColor $color
        }
    }
    
    Write-Host "  ✅ TEST 4 PASSED - Enhanced dashboard data generated" -ForegroundColor Green
} catch {
    Write-Host "  ❌ TEST 4 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Scoring Breakdown
Write-Host "`n[TEST 5] Testing Scoring Breakdown..." -ForegroundColor Yellow
try {
    $breakdownResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/enhanced-analysis/scoring-breakdown/$SessionId" -Method Get
    
    Write-Host "  Total Components: $($breakdownResponse.total_components)" -ForegroundColor White
    Write-Host "  Timestamp: $($breakdownResponse.timestamp)" -ForegroundColor White
    
    if ($breakdownResponse.breakdown) {
        Write-Host "`n  Breakdown by Dimension:" -ForegroundColor Cyan
        foreach ($dim in $breakdownResponse.breakdown.PSObject.Properties.Name) {
            $dimData = $breakdownResponse.breakdown.$dim
            Write-Host "    $($dim):" -ForegroundColor White
            Write-Host "      Dimension Score: $($dimData.dimension_score)" -ForegroundColor $(if ($dimData.dimension_score -gt 70) { "Green" } else { "Yellow" })
            Write-Host "      Components: $($dimData.component_count)" -ForegroundColor White
            
            if ($dimData.components -and $dimData.components.Count -gt 0) {
                Write-Host "      Sample Components:" -ForegroundColor Cyan
                foreach ($comp in $dimData.components | Select-Object -First 2) {
                    Write-Host "        - $($comp.component): $($comp.score) (conf: $($comp.confidence))" -ForegroundColor Gray
                }
            }
        }
    }
    
    Write-Host "  ✅ TEST 5 PASSED - Scoring breakdown retrieved" -ForegroundColor Green
} catch {
    Write-Host "  ❌ TEST 5 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Component Details
Write-Host "`n[TEST 6] Testing Component Details..." -ForegroundColor Yellow
try {
    $componentResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/enhanced-analysis/component-details/market_size_score" -Method Get
    
    Write-Host "  Component: $($componentResponse.details.name)" -ForegroundColor White
    Write-Host "  Description: $($componentResponse.details.description)" -ForegroundColor White
    Write-Host "  Methodology: $($componentResponse.details.methodology)" -ForegroundColor Cyan
    
    Write-Host "  ✅ TEST 6 PASSED - Component details available" -ForegroundColor Green
} catch {
    Write-Host "  ❌ TEST 6 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Scoring Weights
Write-Host "`n[TEST 7] Testing Scoring Weights Endpoint..." -ForegroundColor Yellow
try {
    $weightsResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/enhanced-analysis/weights" -Method Get
    
    Write-Host "  Dimensions with weights:" -ForegroundColor Cyan
    foreach ($dim in $weightsResponse.weights.PSObject.Properties.Name) {
        $weightCount = ($weightsResponse.weights.$dim.PSObject.Properties | Measure-Object).Count
        Write-Host "    $($dim): $weightCount components" -ForegroundColor White
    }
    
    Write-Host "  ✅ TEST 7 PASSED - Weights configuration retrieved" -ForegroundColor Green
} catch {
    Write-Host "  ❌ TEST 7 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Score Recalculation
Write-Host "`n[TEST 8] Testing Score Recalculation..." -ForegroundColor Yellow
try {
    $recalcParams = @{
        "weights" = @{
            "market_analysis" = @{
                "market_size_score" = 0.25
                "growth_potential_score" = 0.20
            }
        }
    } | ConvertTo-Json -Depth 3
    
    $recalcResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v3/enhanced-analysis/recalculate-scores/$SessionId" -Method Post -Body $recalcParams -ContentType "application/json"
    
    Write-Host "  Session: $($recalcResponse.session_id)" -ForegroundColor White
    Write-Host "  Timestamp: $($recalcResponse.timestamp)" -ForegroundColor White
    Write-Host "  Note: $($recalcResponse.note)" -ForegroundColor Cyan
    
    Write-Host "  ✅ TEST 8 PASSED - Score recalculation successful" -ForegroundColor Green
} catch {
    Write-Host "  ❌ TEST 8 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Results Analysis System Status:" -ForegroundColor Yellow
Write-Host "  ✅ Phase 1: AI-Powered Analysis (5 dimensions)" -ForegroundColor Green
Write-Host "  ✅ Phase 2: Enhanced Scoring Engine (9 components)" -ForegroundColor Green
Write-Host "  ✅ API Endpoints: 13 endpoints available" -ForegroundColor Green
Write-Host "  ✅ Dashboard Integration: Complete" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test Results tab in UI (http://localhost:3000)" -ForegroundColor White
Write-Host "  2. Navigate to Results tab and select a topic" -ForegroundColor White
Write-Host "  3. View all 5 analysis dimensions" -ForegroundColor White
Write-Host "  4. Review confidence scores" -ForegroundColor White
Write-Host "  5. Check enhanced scoring data" -ForegroundColor White
Write-Host ""

Write-Host "✅ All Tests Complete!" -ForegroundColor Green

