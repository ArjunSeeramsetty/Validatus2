-- Cloud Spanner schema for analytics and results
-- This schema focuses on global analytics and cross-topic insights

-- Analysis results with global distribution
CREATE TABLE analysis_results (
    session_id STRING(50) NOT NULL,
    analysis_id STRING(50) NOT NULL,
    analysis_type STRING(50) NOT NULL,
    user_id STRING(100) NOT NULL,
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
    
    -- Core scoring results
    overall_score FLOAT64,
    confidence_score FLOAT64,
    
    -- Detailed factor scores stored as JSON
    factor_scores JSON,
    
    -- Segment analysis results
    segment_scores JSON,
    
    -- Expert persona analysis
    expert_analysis JSON,
    
    -- Market insights
    market_insights JSON,
    
    -- Competitive analysis
    competitive_analysis JSON,
    
    -- Metadata and processing info
    processing_metadata JSON,
    
    -- Performance metrics
    processing_time_ms INT64,
    data_points_analyzed INT64,
    
    PRIMARY KEY (session_id, analysis_id)
) PARTITION BY DATE(created_at);

-- Cross-topic insights for pattern recognition
CREATE TABLE cross_topic_insights (
    insight_id STRING(50) NOT NULL,
    user_id STRING(100) NOT NULL,
    insight_type STRING(50) NOT NULL,
    topic_sessions ARRAY<STRING(50)>,
    
    -- Insight data
    insight_data JSON,
    confidence_score FLOAT64,
    supporting_evidence JSON,
    
    -- Temporal information
    time_period_start DATE,
    time_period_end DATE,
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
    
    -- Status and validation
    validation_status STRING(20) DEFAULT 'pending',
    validated_by STRING(100),
    validated_at TIMESTAMP,
    
    PRIMARY KEY (user_id, insight_id)
);

-- Global market intelligence aggregations
CREATE TABLE market_intelligence (
    intelligence_id STRING(50) NOT NULL,
    market_segment STRING(100) NOT NULL,
    time_period DATE NOT NULL,
    
    -- Aggregated metrics
    total_analyses INT64,
    average_scores JSON,
    trend_indicators JSON,
    
    -- Market-wide insights
    emerging_patterns JSON,
    competitive_landscape JSON,
    opportunity_indicators JSON,
    
    -- Data quality metrics
    data_coverage_score FLOAT64,
    source_diversity_score FLOAT64,
    
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
    
    PRIMARY KEY (market_segment, time_period, intelligence_id)
);

-- User analytics for personalization
CREATE TABLE user_analytics (
    user_id STRING(100) NOT NULL,
    metric_date DATE NOT NULL,
    
    -- Usage statistics
    topics_created INT64 DEFAULT 0,
    analyses_completed INT64 DEFAULT 0,
    total_urls_processed INT64 DEFAULT 0,
    
    -- Performance metrics
    average_analysis_quality FLOAT64,
    preferred_analysis_types ARRAY<STRING(50)>,
    most_analyzed_sectors ARRAY<STRING(100)>,
    
    -- Behavioral patterns
    usage_patterns JSON,
    success_indicators JSON,
    
    -- Engagement metrics
    session_duration_avg_minutes FLOAT64,
    features_used ARRAY<STRING(100)>,
    
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
    
    PRIMARY KEY (user_id, metric_date)
);

-- Secondary indexes for efficient querying
CREATE INDEX idx_analysis_results_user_type ON analysis_results (user_id, analysis_type, created_at DESC);
CREATE INDEX idx_analysis_results_confidence ON analysis_results (confidence_score DESC) WHERE confidence_score IS NOT NULL;
CREATE INDEX idx_cross_topic_insights_type ON cross_topic_insights (insight_type, created_at DESC);
CREATE INDEX idx_market_intelligence_segment ON market_intelligence (market_segment, created_at DESC);
CREATE INDEX idx_user_analytics_activity ON user_analytics (topics_created DESC, analyses_completed DESC);
