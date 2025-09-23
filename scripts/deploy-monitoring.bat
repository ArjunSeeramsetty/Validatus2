@echo off
REM Deploy GCP Monitoring Dashboard and Alert Policies for Validatus Platform
REM This script creates comprehensive monitoring infrastructure for the Validatus platform

echo ========================================
echo Validatus Monitoring Deployment Script
echo ========================================
echo.

REM Check if gcloud is installed
gcloud version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Google Cloud SDK is not installed or not in PATH
    echo Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Check if user is authenticated
gcloud auth list --filter=status:ACTIVE --format="value(account)" | findstr /C:"@" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Not authenticated with Google Cloud
    echo Please run: gcloud auth login
    pause
    exit /b 1
)

REM Set project ID
set PROJECT_ID=validatus-prod
echo Setting project to: %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Check if project exists and user has access
gcloud projects describe %PROJECT_ID% >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Project %PROJECT_ID% not found or access denied
    echo Please check your project ID and permissions
    pause
    exit /b 1
)

echo.
echo ========================================
echo Creating Custom Metrics
echo ========================================

REM Create custom metrics for Validatus
echo Creating custom metrics...

REM Analysis Sessions Created
gcloud logging metrics create validatus_analysis_sessions_created ^
    --description="Number of analysis sessions created" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=analysis_session_created" ^
    --metric-type=custom.googleapis.com/validatus/analysis_sessions_created

REM Topics Created
gcloud logging metrics create validatus_topics_created ^
    --description="Number of topics created" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=topic_created" ^
    --metric-type=custom.googleapis.com/validatus/topics_created

REM Content Quality Scores
gcloud logging metrics create validatus_content_quality_scores ^
    --description="Average content quality scores" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=content_quality_analyzed" ^
    --metric-type=custom.googleapis.com/validatus/content_quality_scores ^
    --value-extractor="EXTRACT(jsonPayload.quality_score)"

REM Analysis Session Failures
gcloud logging metrics create validatus_analysis_session_failures ^
    --description="Number of failed analysis sessions" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=analysis_session_failed" ^
    --metric-type=custom.googleapis.com/validatus/analysis_session_failures

REM URLs Processed
gcloud logging metrics create validatus_urls_processed ^
    --description="Number of URLs processed" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=urls_processed" ^
    --metric-type=custom.googleapis.com/validatus/urls_processed

REM Vector Embeddings Generated
gcloud logging metrics create validatus_vector_embeddings_generated ^
    --description="Number of vector embeddings generated" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=vector_embeddings_generated" ^
    --metric-type=custom.googleapis.com/validatus/vector_embeddings_generated

REM Expert Persona Analyses
gcloud logging metrics create validatus_expert_persona_analyses ^
    --description="Number of expert persona analyses performed" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=expert_persona_analysis_completed" ^
    --metric-type=custom.googleapis.com/validatus/expert_persona_analyses

echo.
echo ========================================
echo Creating Notification Channels
echo ========================================

REM Create email notification channel
echo Creating email notification channel...
gcloud alpha monitoring channels create ^
    --display-name="Email Alerts" ^
    --type=email ^
    --channel-labels=email_address=alerts@validatus.ai

REM Create Slack notification channel (if webhook URL is provided)
if not "%SLACK_WEBHOOK_URL%"=="" (
    echo Creating Slack notification channel...
    gcloud alpha monitoring channels create ^
        --display-name="Slack Alerts" ^
        --type=slack ^
        --channel-labels=channel_name=#validatus-alerts,webhook_url=%SLACK_WEBHOOK_URL%
)

echo.
echo ========================================
echo Creating Alert Policies
echo ========================================

REM Create high error rate alert policy
echo Creating high error rate alert policy...
gcloud alpha monitoring policies create ^
    --policy-from-file=infrastructure/monitoring/alert_policy_high_error_rate.yaml

REM Create high response time alert policy
echo Creating high response time alert policy...
gcloud alpha monitoring policies create ^
    --policy-from-file=infrastructure/monitoring/alert_policy_high_response_time.yaml

REM Create high memory usage alert policy
echo Creating high memory usage alert policy...
gcloud alpha monitoring policies create ^
    --policy-from-file=infrastructure/monitoring/alert_policy_high_memory.yaml

REM Create analysis session failures alert policy
echo Creating analysis session failures alert policy...
gcloud alpha monitoring policies create ^
    --policy-from-file=infrastructure/monitoring/alert_policy_analysis_failures.yaml

echo.
echo ========================================
echo Creating Monitoring Dashboard
echo ========================================

REM Create monitoring dashboard
echo Creating monitoring dashboard...
gcloud monitoring dashboards create ^
    --config-from-file=infrastructure/monitoring/dashboard_config.yaml

echo.
echo ========================================
echo Creating Log-Based Metrics
echo ========================================

REM Create log-based metrics for better observability
echo Creating log-based metrics...

REM API Request Metrics
gcloud logging metrics create api_requests_by_endpoint ^
    --description="API requests by endpoint" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.message=~\"API request\"" ^
    --metric-type=custom.googleapis.com/validatus/api_requests_by_endpoint

REM Analysis Duration Metrics
gcloud logging metrics create analysis_duration ^
    --description="Analysis session duration" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=analysis_completed" ^
    --metric-type=custom.googleapis.com/validatus/analysis_duration ^
    --value-extractor="EXTRACT(jsonPayload.duration_seconds)"

REM Content Processing Metrics
gcloud logging metrics create content_processing_time ^
    --description="Content processing time" ^
    --log-filter="resource.type=cloud_run_revision AND jsonPayload.event=content_processed" ^
    --metric-type=custom.googleapis.com/validatus/content_processing_time ^
    --value-extractor="EXTRACT(jsonPayload.processing_time_seconds)"

echo.
echo ========================================
echo Setting up Uptime Checks
echo ========================================

REM Create uptime check for health endpoint
echo Creating uptime check for health endpoint...
gcloud monitoring uptime create ^
    --display-name="Validatus Health Check" ^
    --http-check-path="/health" ^
    --host="validatus-backend-validatus-prod.run.app" ^
    --check-interval="60s" ^
    --timeout="10s"

REM Create uptime check for API endpoints
echo Creating uptime check for API endpoints...
gcloud monitoring uptime create ^
    --display-name="Validatus API Check" ^
    --http-check-path="/api/v3/topics" ^
    --host="validatus-backend-validatus-prod.run.app" ^
    --check-interval="300s" ^
    --timeout="30s"

echo.
echo ========================================
echo Creating Service Monitoring
echo ========================================

REM Create service monitoring for Cloud Run
echo Creating service monitoring...
gcloud monitoring services create ^
    --display-name="Validatus Backend Service" ^
    --service-type=cloud_run_revision ^
    --service-labels=service_name=validatus-backend

echo.
echo ========================================
echo Verifying Deployment
echo ========================================

REM List created metrics
echo Listing created custom metrics...
gcloud logging metrics list --filter="name:validatus"

REM List created alert policies
echo Listing created alert policies...
gcloud alpha monitoring policies list --filter="displayName:Validatus"

REM List created dashboards
echo Listing created dashboards...
gcloud monitoring dashboards list --filter="displayName:Validatus"

REM List created uptime checks
echo Listing created uptime checks...
gcloud monitoring uptime list --filter="displayName:Validatus"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Monitoring infrastructure has been successfully deployed:
echo.
echo - Custom metrics created for business and technical KPIs
echo - Alert policies configured for critical thresholds
echo - Comprehensive monitoring dashboard deployed
echo - Uptime checks established for service availability
echo - Notification channels configured for alerts
echo.
echo Access your monitoring dashboard at:
echo https://console.cloud.google.com/monitoring/dashboards?project=%PROJECT_ID%
echo.
echo To view logs and metrics:
echo https://console.cloud.google.com/logs/query?project=%PROJECT_ID%
echo https://console.cloud.google.com/monitoring?project=%PROJECT_ID%
echo.
echo Next steps:
echo 1. Configure additional notification channels as needed
echo 2. Customize alert thresholds based on your requirements
echo 3. Set up additional uptime checks for critical endpoints
echo 4. Review and adjust dashboard widgets for your use case
echo.
pause
