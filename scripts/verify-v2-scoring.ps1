# ========================================
# V2.0 SCORING SYSTEM VERIFICATION SCRIPT
# ========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "V2.0 SCORING SYSTEM - VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Check Backend Deployment Status
Write-Host "[1] Checking Backend Deployment Status..." -ForegroundColor Yellow
gcloud run services describe validatus-backend `
    --region=us-central1 `
    --project=validatus-platform `
    --format="value(status.url,status.conditions[0].status,metadata.generation)"

# 2. Check if V2.0 Configuration is Loaded
Write-Host "`n[2] Checking V2.0 Configuration in Logs..." -ForegroundColor Yellow
gcloud logging read `
    'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND textPayload:"v2.0"' `
    --limit 10 `
    --project=validatus-platform `
    --format='value(timestamp,textPayload)' `
    --freshness=1h

# 3. Check Database Tables Exist
Write-Host "`n[3] Checking V2.0 Database Tables..." -ForegroundColor Yellow
Write-Host "Connecting to Cloud SQL (you may need to enter password: validatus_secure_2024)..." -ForegroundColor Gray
$checkTablesQuery = @"
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('segments', 'factors', 'layers', 'layer_scores', 'v2_analysis_results')
ORDER BY table_name;
"@

Write-Host "Run this query manually:" -ForegroundColor Gray
Write-Host $checkTablesQuery -ForegroundColor White

# 4. Check for Recent V2.0 Analysis Results
Write-Host "`n[4] Checking for Recent V2.0 Analysis Results..." -ForegroundColor Yellow
$resultsQuery = @"
SELECT session_id, layers_analyzed, factors_calculated, segments_evaluated, created_at 
FROM v2_analysis_results 
ORDER BY created_at DESC 
LIMIT 5;
"@

Write-Host "Run this query to check results:" -ForegroundColor Gray
Write-Host $resultsQuery -ForegroundColor White

# 5. Test V2.0 API Endpoints
Write-Host "`n[5] Testing V2.0 API Endpoints..." -ForegroundColor Yellow
$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

Write-Host "Testing GET $backendUrl/api/v3/v2-scoring/configuration" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "$backendUrl/api/v3/v2-scoring/configuration" -Method Get
    Write-Host "✅ V2.0 Configuration API working!" -ForegroundColor Green
    Write-Host "   Segments: $($response.segments)" -ForegroundColor White
    Write-Host "   Factors: $($response.factors)" -ForegroundColor White
    Write-Host "   Layers: $($response.layers)" -ForegroundColor White
} catch {
    Write-Host "❌ V2.0 Configuration API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Check Topics Available for Scoring
Write-Host "`n[6] Checking Topics Available for Scoring..." -ForegroundColor Yellow
Write-Host "Testing GET $backendUrl/api/v3/scoring/topics" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/topics" -Method Get
    Write-Host "✅ Topics API working!" -ForegroundColor Green
    Write-Host "   Total topics: $($response.topics.Count)" -ForegroundColor White
    
    if ($response.topics.Count -gt 0) {
        Write-Host "`n   Available topics:" -ForegroundColor White
        foreach ($topic in $response.topics) {
            $contentCount = $topic.content_statistics.total_items
            $scoringStatus = $topic.scoring_information.scoring_status
            Write-Host "   - $($topic.session_id): $($topic.topic)" -ForegroundColor Cyan
            Write-Host "     Content: $contentCount items | Status: $scoringStatus" -ForegroundColor Gray
        }
        
        # Save first session_id for testing
        $script:testSessionId = $response.topics[0].session_id
        Write-Host "`n   Test Session ID: $script:testSessionId" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Topics API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Instructions for Manual Testing
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "MANUAL TESTING INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "To test V2.0 scoring with a real topic:" -ForegroundColor Yellow
Write-Host ""
if ($script:testSessionId) {
    Write-Host "1. Start scoring analysis:" -ForegroundColor White
    Write-Host "   Invoke-RestMethod -Uri '$backendUrl/api/v3/scoring/$script:testSessionId/start' -Method Post" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Check status (run this after 5-10 minutes):" -ForegroundColor White
    Write-Host "   Invoke-RestMethod -Uri '$backendUrl/api/v3/scoring/$script:testSessionId/status' -Method Get" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Get results (when status is 'completed'):" -ForegroundColor White
    Write-Host "   Invoke-RestMethod -Uri '$backendUrl/api/v3/scoring/$script:testSessionId/results' -Method Get" -ForegroundColor Gray
} else {
    Write-Host "   No topics with content found. Please scrape content first!" -ForegroundColor Red
}

# 8. Check Recent Backend Logs
Write-Host "`n[8] Checking Recent Backend Logs..." -ForegroundColor Yellow
Write-Host "Last 20 log entries:" -ForegroundColor Gray
gcloud logging read `
    'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend' `
    --limit 20 `
    --project=validatus-platform `
    --format='value(timestamp,severity,textPayload)' `
    --freshness=30m

# 9. Database Connection Helper
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DATABASE CONNECTION HELPER" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "To connect to the database manually:" -ForegroundColor Yellow
Write-Host "gcloud sql connect validatus-sql --user=postgres --project=validatus-platform --database=validatus" -ForegroundColor White
Write-Host "Password: validatus_secure_2024" -ForegroundColor Gray
Write-Host ""
Write-Host "Useful queries once connected:" -ForegroundColor Yellow
Write-Host "- Count layers: SELECT COUNT(*) FROM layers;" -ForegroundColor Gray
Write-Host "- Count factors: SELECT COUNT(*) FROM factors;" -ForegroundColor Gray
Write-Host "- Count segments: SELECT COUNT(*) FROM segments;" -ForegroundColor Gray
Write-Host "- Check v2 results: SELECT session_id, layers_analyzed, created_at FROM v2_analysis_results;" -ForegroundColor Gray

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "VERIFICATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

