# ========================================
# V2.0 ANALYSIS MONITORING SCRIPT
# ========================================
# Usage: .\monitor-v2-analysis.ps1 -SessionId "topic-xxxxx"
# This script continuously monitors the progress of a V2.0 analysis

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [int]$CheckIntervalSeconds = 60
)

$backendUrl = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "V2.0 ANALYSIS MONITOR" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "Session ID: $SessionId" -ForegroundColor White
Write-Host "Check Interval: $CheckIntervalSeconds seconds" -ForegroundColor White
Write-Host "Press Ctrl+C to stop monitoring`n" -ForegroundColor Gray

$startTime = Get-Date
$checkCount = 0

while ($true) {
    $checkCount++
    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
    
    Write-Host "[$checkCount] Checking status (elapsed: $elapsed min)..." -ForegroundColor Yellow
    
    try {
        $statusResponse = Invoke-RestMethod -Uri "$backendUrl/api/v3/scoring/$SessionId/status" -Method Get
        
        Write-Host "   Status: " -NoNewline -ForegroundColor White
        
        switch ($statusResponse.status) {
            "completed" {
                Write-Host "$($statusResponse.status)" -ForegroundColor Green
                Write-Host "   ✅ Analysis completed!" -ForegroundColor Green
                Write-Host "   Analysis Type: $($statusResponse.analysis_type)" -ForegroundColor White
                
                if ($statusResponse.layers_analyzed) {
                    Write-Host "   Layers analyzed: $($statusResponse.layers_analyzed)" -ForegroundColor White
                }
                
                Write-Host "   Completed at: $($statusResponse.completed_at)" -ForegroundColor White
                
                Write-Host "`n========================================" -ForegroundColor Cyan
                Write-Host "ANALYSIS COMPLETE!" -ForegroundColor Green
                Write-Host "========================================`n" -ForegroundColor Cyan
                
                Write-Host "Get results:" -ForegroundColor Yellow
                Write-Host "Invoke-RestMethod -Uri '$backendUrl/api/v3/scoring/$SessionId/results' -Method Get" -ForegroundColor White
                
                exit 0
            }
            "in_progress" {
                Write-Host "$($statusResponse.status)" -ForegroundColor Yellow
                Write-Host "   ⏳ Analysis in progress..." -ForegroundColor Yellow
                if ($statusResponse.message) {
                    Write-Host "   Message: $($statusResponse.message)" -ForegroundColor White
                }
            }
            "failed" {
                Write-Host "$($statusResponse.status)" -ForegroundColor Red
                Write-Host "   ❌ Analysis failed!" -ForegroundColor Red
                if ($statusResponse.error) {
                    Write-Host "   Error: $($statusResponse.error)" -ForegroundColor White
                }
                exit 1
            }
            "not_started" {
                Write-Host "$($statusResponse.status)" -ForegroundColor Gray
                Write-Host "   ⚠️  Analysis not started yet" -ForegroundColor Gray
            }
            default {
                Write-Host "$($statusResponse.status)" -ForegroundColor White
            }
        }
        
    } catch {
        Write-Host "   ❌ Error checking status: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Check recent logs
    Write-Host "   Checking recent logs..." -ForegroundColor Gray
    try {
        $logs = gcloud logging read `
            "resource.type=cloud_run_revision AND resource.labels.service_name=validatus-backend AND textPayload:""$SessionId""" `
            --limit 5 `
            --project=validatus-platform `
            --format='value(textPayload)' `
            --freshness=5m 2>$null
        
        if ($logs) {
            $logLines = $logs -split "`n" | Select-Object -First 3
            foreach ($line in $logLines) {
                if (-not [string]::IsNullOrWhiteSpace($line)) {
                    $shortLog = if ($line.Length -gt 80) { $line.Substring(0, 77) + "..." } else { $line }
                    Write-Host "     $shortLog" -ForegroundColor DarkGray
                }
            }
        }
    } catch {
        # Silently ignore log fetch errors
    }
    
    Write-Host "   Next check in $CheckIntervalSeconds seconds..." -ForegroundColor DarkGray
    Write-Host ""
    
    Start-Sleep -Seconds $CheckIntervalSeconds
}

