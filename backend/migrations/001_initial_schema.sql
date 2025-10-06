-- Initial Schema Creation for Validatus Platform
-- Migration 001: Create base tables

-- Create topics table first (referenced by other tables)
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    topic VARCHAR(500) NOT NULL,
    description TEXT,
    user_id VARCHAR(100) NOT NULL,
    analysis_type VARCHAR(50) DEFAULT 'comprehensive',
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create topic_urls table
CREATE TABLE IF NOT EXISTS topic_urls (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    content_hash VARCHAR(64),
    scraped_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_topic_urls_session_id 
        FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE
);

-- Create workflow_status table
CREATE TABLE IF NOT EXISTS workflow_status (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_workflow_status_session_id 
        FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate stage entries per session
    CONSTRAINT unique_session_stage UNIQUE (session_id, stage)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_topics_session_id ON topics(session_id);
CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
CREATE INDEX IF NOT EXISTS idx_topic_urls_session_id ON topic_urls(session_id);
CREATE INDEX IF NOT EXISTS idx_topic_urls_status ON topic_urls(status);
CREATE INDEX IF NOT EXISTS idx_workflow_status_session_id ON workflow_status(session_id);
CREATE INDEX IF NOT EXISTS idx_workflow_status_stage ON workflow_status(stage);

-- Create validatus_app user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'validatus_app') THEN
        CREATE USER validatus_app WITH PASSWORD 'temp_password';
    END IF;
END
$$;

-- Grant permissions to validatus_app user
GRANT SELECT, INSERT, UPDATE, DELETE ON topics TO validatus_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON topic_urls TO validatus_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON workflow_status TO validatus_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO validatus_app;