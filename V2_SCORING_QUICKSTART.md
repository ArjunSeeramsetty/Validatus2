# V2.0 Scoring System - Quick Start Guide

## 🚀 PowerShell Quick Commands

### 1. Verify V2.0 System is Running

```powershell
# Run comprehensive verification
.\scripts\verify-v2-scoring.ps1

# Check backend deployment
gcloud run services describe validatus-backend --region=us-central1 --project=validatus-platform --format="value(status.url,status.conditions[0].status)"

# Check v2.0 configuration loaded
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND textPayload:"v2.0"' --limit 5 --project=validatus-platform --format='value(timestamp,textPayload)' --freshness=1h
```

### 2. List Available Topics

```powershell
# Using API
$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
$topics = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/topics" -Method Get
$topics.topics | Format-Table session_id, topic, @{Name='Content';Expression={$_.content_statistics.total_items}}, @{Name='Status';Expression={$_.scoring_information.scoring_status}}
```

### 3. Start V2.0 Scoring Analysis

```powershell
# Automated test (finds topic automatically)
.\scripts\test-v2-scoring.ps1

# Manual test with specific session ID
$sessionId = "topic-xxxxx"
$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/$sessionId/start" -Method Post
```

### 4. Check Analysis Status

```powershell
# Check once
$sessionId = "topic-xxxxx"
$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/$sessionId/status" -Method Get

# Monitor continuously (checks every 60 seconds)
.\scripts\monitor-v2-analysis.ps1 -SessionId "topic-xxxxx"

# Monitor with faster checks (every 30 seconds)
.\scripts\monitor-v2-analysis.ps1 -SessionId "topic-xxxxx" -CheckIntervalSeconds 30
```

### 5. Get Analysis Results

```powershell
# Get complete results
$sessionId = "topic-xxxxx"
$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
$results = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/$sessionId/results" -Method Get

# Display results
$results | ConvertTo-Json -Depth 5

# Extract key metrics
Write-Host "Business Case Score: $($results.results.business_case_score)"
Write-Host "Layers Analyzed: $($results.results.summary.layers_analyzed)"
Write-Host "Factors Calculated: $($results.results.summary.factors_calculated)"
Write-Host "Segments Evaluated: $($results.results.summary.segments_evaluated)"
```

### 6. Check Backend Logs

```powershell
# Check recent v2.0 logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND (textPayload:"v2.0" OR textPayload:"V2" OR textPayload:"Gemini")' --limit 30 --project=validatus-platform --format='value(timestamp,severity,textPayload)' --freshness=1h

# Check logs for specific session
$sessionId = "topic-xxxxx"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND textPayload:""$sessionId""" --limit 50 --project=validatus-platform --format='value(timestamp,severity,textPayload)' --freshness=1h

# Check error logs only
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND severity>=ERROR' --limit 20 --project=validatus-platform --format='value(timestamp,severity,textPayload)' --freshness=1h
```

### 7. Database Queries

```powershell
# Connect to database
gcloud sql connect validatus-sql --user=postgres --project=validatus-platform --database=validatus
# Password: validatus_secure_2024

# Once connected, useful queries:
```

```sql
-- Check hierarchy setup
SELECT COUNT(*) as segment_count FROM segments;
SELECT COUNT(*) as factor_count FROM factors;
SELECT COUNT(*) as layer_count FROM layers;

-- Check v2.0 analysis results
SELECT session_id, layers_analyzed, factors_calculated, segments_evaluated, created_at 
FROM v2_analysis_results 
ORDER BY created_at DESC 
LIMIT 10;

-- Check layer scores for a session
SELECT l.layer_name, ls.score, ls.confidence, ls.created_at
FROM layer_scores ls
JOIN layers l ON ls.layer_id = l.id
WHERE ls.session_id = 'topic-xxxxx'
ORDER BY ls.created_at DESC
LIMIT 20;

-- Check which sessions have v2.0 results
SELECT DISTINCT session_id, created_at 
FROM v2_analysis_results 
ORDER BY created_at DESC;
```

## 🎯 Complete Workflow Example

```powershell
# Step 1: Verify system
.\scripts\verify-v2-scoring.ps1

# Step 2: Run test (auto-finds topic with content)
.\scripts\test-v2-scoring.ps1

# Step 3: Monitor progress (copy session ID from step 2)
.\scripts\monitor-v2-analysis.ps1 -SessionId "topic-xxxxx"

# Step 4: When complete, get results
$sessionId = "topic-xxxxx"
$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
$results = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/$sessionId/results" -Method Get
$results | ConvertTo-Json -Depth 5 | Out-File "v2-analysis-results-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
Write-Host "Results saved to file!"
```

## 📊 Frontend Testing

### Using Browser Console

1. Open frontend in browser: https://validatus-frontend-311427723702.us-central1.run.app
2. Navigate to a topic with scraped content
3. Click "Start Scoring" button
4. Open browser DevTools (F12) > Console tab
5. Watch for API calls:
   - POST `/api/v3/scoring/{sessionId}/start`
   - GET `/api/v3/scoring/{sessionId}/status` (polling)
   - GET `/api/v3/scoring/{sessionId}/results` (when complete)

### Expected Behavior

1. **Start**: Should see "Analysis started in background" alert
2. **Status**: Frontend polls every 30 seconds
3. **Complete**: Should see "Analysis completed!" alert after 15-20 minutes
4. **Results**: Click "View Results" to see v2.0 scores

## 🔧 Troubleshooting

### If V2.0 Orchestrator Not Loading

```powershell
# Check for import errors
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND (textPayload:"orchestrator" OR textPayload:"ImportError")' --limit 20 --project=validatus-platform --format='value(timestamp,severity,textPayload)' --freshness=2h
```

### If Gemini API Calls Failing

```powershell
# Check Gemini-related errors
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND (textPayload:"Gemini" OR textPayload:"gemini" OR textPayload:"404" OR textPayload:"503")' --limit 30 --project=validatus-platform --format='value(timestamp,severity,textPayload)' --freshness=1h
```

### If Database Errors

```powershell
# Check for FK violations or database errors
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND (textPayload:"foreign key" OR textPayload:"violates" OR textPayload:"database" OR severity>=ERROR)' --limit 30 --project=validatus-platform --format='value(timestamp,severity,textPayload)' --freshness=1h
```

## 📝 Key Differences: Mock vs V2.0

| Feature | Mock Scoring | V2.0 Real Scoring |
|---------|-------------|-------------------|
| **Layers** | 8 hardcoded | 210 LLM-analyzed |
| **Factors** | 3 calculated | 28 calculated |
| **Segments** | 2 evaluated | 5 evaluated |
| **Processing** | Instant (< 1 sec) | 15-20 minutes |
| **Analysis** | Random numbers | Real Gemini LLM |
| **Status** | Immediate "completed" | "in_progress" → "completed" |
| **Results Table** | `analysis_scores` | `v2_analysis_results` |

## 🎓 Understanding the Results

### Structure

```json
{
  "has_results": true,
  "session_id": "topic-xxxxx",
  "scored_at": "2025-10-10T10:30:00Z",
  "results": {
    "business_case_score": 0.72,
    "segment_scores": {
      "MARKET": { "score": 0.68, "factors": [...] },
      "CAPABILITY": { "score": 0.75, "factors": [...] },
      "EXECUTION": { "score": 0.70, "factors": [...] },
      "SUSTAINABILITY": { "score": 0.73, "factors": [...] },
      "RISK": { "score": 0.66, "factors": [...] }
    },
    "summary": {
      "layers_analyzed": 210,
      "factors_calculated": 28,
      "segments_evaluated": 5,
      "total_processing_time_seconds": 850
    }
  }
}
```

### Score Interpretation

- **0.0 - 0.3**: Poor / High Risk
- **0.3 - 0.5**: Below Average / Significant Concerns
- **0.5 - 0.7**: Average / Moderate Opportunity
- **0.7 - 0.85**: Good / Strong Opportunity
- **0.85 - 1.0**: Excellent / Outstanding Opportunity

## 🔐 Security Notes

- API keys stored in Google Secret Manager
- Database password: `validatus_secure_2024` (change in production!)
- All API endpoints are public (add auth for production)

## 📞 Support

If you encounter issues:

1. Check backend logs: `gcloud logging read ...`
2. Verify database connectivity: `gcloud sql connect ...`
3. Test API endpoints: Use PowerShell `Invoke-RestMethod` commands above
4. Review this guide for troubleshooting steps

