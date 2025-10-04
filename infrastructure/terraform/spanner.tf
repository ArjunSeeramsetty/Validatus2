# Cloud Spanner Instance
resource "google_spanner_instance" "validatus_analytics" {
  config       = "regional-${var.region}"
  display_name = "Validatus Analytics"
  name         = "validatus-analytics"
  
  # Use processing units for cost optimization
  processing_units = 100  # Minimum for production, 1000 PU = 1 node
  
  labels = {
    managed_by  = "terraform"
    environment = var.environment
    service     = "validatus"
    component   = "analytics"
  }

  depends_on = [google_project_service.apis]
}

# Create Spanner Database
resource "google_spanner_database" "validatus_analytics_db" {
  instance = google_spanner_instance.validatus_analytics.name
  name     = "validatus-analytics"
  
  # DDL statements for schema creation
  ddl = [
    <<-EOT
    CREATE TABLE analysis_results (
      session_id STRING(50) NOT NULL,
      analysis_id STRING(50) NOT NULL,
      analysis_type STRING(50) NOT NULL,
      user_id STRING(100) NOT NULL,
      created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
      
      -- Core scoring results
      overall_score FLOAT64,
      confidence_score FLOAT64,
      
      -- Detailed results stored as JSON
      factor_scores JSON,
      segment_scores JSON,
      expert_analysis JSON,
      market_insights JSON,
      competitive_analysis JSON,
      processing_metadata JSON,
      
      -- Performance metrics
      processing_time_ms INT64,
      data_points_analyzed INT64
    ) PRIMARY KEY (session_id, analysis_id)
    EOT
    ,
    <<-EOT
    CREATE TABLE cross_topic_insights (
      insight_id STRING(50) NOT NULL,
      user_id STRING(100) NOT NULL,
      insight_type STRING(50) NOT NULL,
      topic_sessions ARRAY<STRING(50)>,
      insight_data JSON,
      confidence_score FLOAT64,
      created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
      validation_status STRING(20) DEFAULT 'pending'
    ) PRIMARY KEY (user_id, insight_id)
    EOT
    ,
    <<-EOT
    CREATE TABLE user_analytics (
      user_id STRING(100) NOT NULL,
      metric_date DATE NOT NULL,
      topics_created INT64 DEFAULT 0,
      analyses_completed INT64 DEFAULT 0,
      total_urls_processed INT64 DEFAULT 0,
      average_analysis_quality FLOAT64,
      usage_patterns JSON,
      created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true)
    ) PRIMARY KEY (user_id, metric_date)
    EOT
    ,
    # Create indexes
    "CREATE INDEX idx_analysis_results_user_type ON analysis_results (user_id, analysis_type, created_at DESC)",
    "CREATE INDEX idx_cross_topic_insights_type ON cross_topic_insights (insight_type, created_at DESC)",
    "CREATE INDEX idx_user_analytics_activity ON user_analytics (topics_created DESC, analyses_completed DESC)"
  ]

  deletion_protection = false  # Set to true in production
  
  depends_on = [google_spanner_instance.validatus_analytics]
}
