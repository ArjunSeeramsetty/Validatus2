-- Create URL Collection Campaigns Table
-- Migration 002: Create url_collection_campaigns table

CREATE TABLE IF NOT EXISTS url_collection_campaigns (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    campaign_name VARCHAR(200),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_urls_collected INTEGER NOT NULL DEFAULT 0,
    total_queries_processed INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_url_collection_campaigns_session_id 
        FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
    
    -- Check constraints
    CONSTRAINT chk_campaign_status 
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_url_collection_campaigns_session_id 
    ON url_collection_campaigns(session_id);

CREATE INDEX IF NOT EXISTS idx_url_collection_campaigns_status 
    ON url_collection_campaigns(status);

-- Add Google Custom Search specific columns
ALTER TABLE url_collection_campaigns 
ADD COLUMN IF NOT EXISTS search_api_used VARCHAR(50) DEFAULT 'google_custom_search',
ADD COLUMN IF NOT EXISTS api_quota_used INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS search_language VARCHAR(10) DEFAULT 'en',
ADD COLUMN IF NOT EXISTS safe_search_level VARCHAR(20) DEFAULT 'medium';

-- Create search_queries table
CREATE TABLE IF NOT EXISTS search_queries (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    campaign_id INTEGER,
    query_text TEXT NOT NULL,
    results_count INTEGER DEFAULT 0,
    api_quota_used INTEGER DEFAULT 0,
    executed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_search_queries_session_id 
        FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_search_queries_campaign_id 
        FOREIGN KEY (campaign_id) REFERENCES url_collection_campaigns(id) ON DELETE CASCADE
);

-- Create index for search_queries
CREATE INDEX IF NOT EXISTS idx_search_queries_session_id 
    ON search_queries(session_id);

CREATE INDEX IF NOT EXISTS idx_search_queries_campaign_id 
    ON search_queries(campaign_id);

-- Add Google Custom Search specific columns to topic_urls table
ALTER TABLE topic_urls 
ADD COLUMN IF NOT EXISTS search_rank INTEGER,
ADD COLUMN IF NOT EXISTS search_query TEXT,
ADD COLUMN IF NOT EXISTS snippet TEXT,
ADD COLUMN IF NOT EXISTS formatted_url TEXT;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_topic_urls_search_rank 
    ON topic_urls(search_rank);

-- Create url_collection_summary view
CREATE OR REPLACE VIEW url_collection_summary AS
SELECT 
    t.session_id,
    t.topic,
    t.user_id,
    t.created_at as topic_created_at,
    ucc.status as collection_status,
    ucc.total_urls_collected,
    ucc.total_queries_processed,
    ucc.started_at,
    ucc.completed_at,
    ucc.error_message,
    COUNT(tu.id) as actual_urls_in_db
FROM topics t
LEFT JOIN url_collection_campaigns ucc ON t.session_id = ucc.session_id
LEFT JOIN topic_urls tu ON t.session_id = tu.session_id
GROUP BY t.session_id, t.topic, t.user_id, t.created_at, ucc.status, 
         ucc.total_urls_collected, ucc.total_queries_processed, 
         ucc.started_at, ucc.completed_at, ucc.error_message;

-- Grant permissions to validatus_app user
GRANT SELECT, INSERT, UPDATE, DELETE ON url_collection_campaigns TO validatus_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON search_queries TO validatus_app;
GRANT SELECT ON url_collection_summary TO validatus_app;
GRANT USAGE, SELECT ON SEQUENCE url_collection_campaigns_id_seq TO validatus_app;
GRANT USAGE, SELECT ON SEQUENCE search_queries_id_seq TO validatus_app;
