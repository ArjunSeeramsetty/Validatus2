# ========================================
# QUICK V2.0 SCORING TEST SCRIPT
# ========================================
# Usage: .\test-v2-scoring.ps1 -SessionId "topic-xxxxx"

param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId = ""
)

$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "V2.0 SCORING - QUICK TEST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# If no session ID provided, get available topics
if ([string]::IsNullOrEmpty($SessionId)) {
    Write-Host "No Session ID provided. Fetching available topics..." -ForegroundColor Yellow
    
    try {
        $topicsResponse = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/topics" -Method Get
        
        if ($topicsResponse.topics.Count -eq 0) {
            Write-Host "❌ No topics found. Please create a topic and scrape content first." -ForegroundColor Red
            exit 1
        }
        
        Write-Host "`nAvailable topics:" -ForegroundColor Green
        for ($i = 0; $i -lt $topicsResponse.topics.Count; $i++) {
            $topic = $topicsResponse.topics[$i]
            $contentCount = $topic.content_statistics.total_items
            $status = $topic.scoring_information.scoring_status
            Write-Host "[$i] $($topic.session_id)" -ForegroundColor Cyan
            Write-Host "    Topic: $($topic.topic)" -ForegroundColor White
            Write-Host "    Content: $contentCount items | Status: $status" -ForegroundColor Gray
        }
        
        # Use first topic with content
        $selectedTopic = $topicsResponse.topics | Where-Object { $_.content_statistics.total_items -gt 0 } | Select-Object -First 1
        
        if ($null -eq $selectedTopic) {
            Write-Host "`n❌ No topics with scraped content found!" -ForegroundColor Red
            Write-Host "   Please scrape content for a topic first." -ForegroundColor Yellow
            exit 1
        }
        
        $SessionId = $selectedTopic.session_id
        Write-Host "`n✅ Selected: $SessionId" -ForegroundColor Green
        Write-Host "   Topic: $($selectedTopic.topic)" -ForegroundColor White
        Write-Host "   Content items: $($selectedTopic.content_statistics.total_items)" -ForegroundColor White
        
    } catch {
        Write-Host "❌ Failed to fetch topics: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Step 1: Start Scoring
Write-Host "`n[1] Starting V2.0 Scoring Analysis..." -ForegroundColor Yellow
try {
    $startResponse = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/$SessionId/start" -Method Post
    
    if ($startResponse.success) {
        Write-Host "✅ Scoring started successfully!" -ForegroundColor Green
        Write-Host "   Analysis Type: $($startResponse.analysis_type)" -ForegroundColor White
        Write-Host "   Status: $($startResponse.status)" -ForegroundColor White
        
        if ($startResponse.status -eq "in_progress") {
            Write-Host "   Layers to analyze: $($startResponse.layers_to_analyze)" -ForegroundColor White
            Write-Host "   Estimated time: $($startResponse.estimated_time_minutes) minutes" -ForegroundColor White
            Write-Host "`n   💡 $($startResponse.message)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Failed to start scoring: $($startResponse.error)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error starting scoring: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Wait a bit and check status
Write-Host "`n[2] Waiting 10 seconds before checking status..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "[3] Checking Status..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/$SessionId/status" -Method Get
    
    Write-Host "   Status: $($statusResponse.status)" -ForegroundColor White
    Write-Host "   Analysis Type: $($statusResponse.analysis_type)" -ForegroundColor White
    
    if ($statusResponse.status -eq "completed") {
        Write-Host "   ✅ Analysis completed!" -ForegroundColor Green
        Write-Host "   Layers analyzed: $($statusResponse.layers_analyzed)" -ForegroundColor White
        Write-Host "   Completed at: $($statusResponse.completed_at)" -ForegroundColor White
    } elseif ($statusResponse.status -eq "in_progress") {
        Write-Host "   ⏳ Analysis still in progress..." -ForegroundColor Yellow
        Write-Host "   Message: $($statusResponse.message)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Error checking status: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Instructions for getting results
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($statusResponse.status -eq "completed") {
    Write-Host "✅ Analysis is complete! Get results:" -ForegroundColor Green
    Write-Host "   `$results = Invoke-RestMethod -Uri '$backendUrl/api/v3/scoring/$SessionId/results' -Method Get" -ForegroundColor White
    Write-Host "   `$results | ConvertTo-Json -Depth 5" -ForegroundColor White
} else {
    Write-Host "⏳ Analysis is still running. Check status again in 10-15 minutes:" -ForegroundColor Yellow
    Write-Host "   Invoke-RestMethod -Uri '$backendUrl/api/v3/scoring/$SessionId/status' -Method Get" -ForegroundColor White
    Write-Host ""
    Write-Host "   When complete, get results:" -ForegroundColor Yellow
    Write-Host "   Invoke-RestMethod -Uri '$backendUrl/api/v3/scoring/$SessionId/results' -Method Get" -ForegroundColor White
}

# Step 4: Check Backend Logs
Write-Host "`n[4] Checking Recent Backend Logs..." -ForegroundColor Yellow
Write-Host "Looking for v2.0 analysis activity..." -ForegroundColor Gray

gcloud logging read `
    "resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND textPayload:""$SessionId""" `
    --limit 15 `
    --project=validatus-platform `
    --format='value(timestamp,severity,textPayload)' `
    --freshness=5m

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Session ID: $SessionId" -ForegroundColor Cyan
Write-Host "Use this ID to check status and results." -ForegroundColor White

