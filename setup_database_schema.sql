-- Validatus Database Schema
-- Simple setup for production

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Topics table (main entity)
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    topic VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
    CONSTRAINT topics_status_check CHECK (status IN ('CREATED', 'PROCESSING', 'COMPLETED', 'FAILED')),
    analysis_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
    CONSTRAINT topics_analysis_type_check CHECK (analysis_type IN ('comprehensive', 'quick', 'detailed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    search_queries TEXT[],
    initial_urls TEXT[]
);

-- URLs table for tracking URL collection and processing
CREATE TABLE IF NOT EXISTS topic_urls (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    CONSTRAINT fk_topic_urls_session FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    source VARCHAR(100) NOT NULL DEFAULT 'unknown',
    status VARCHAR(50) DEFAULT 'pending',
    CONSTRAINT topic_urls_status_check CHECK (status IN ('pending', 'scraped', 'failed')),
    quality_score DECIMAL(3,2),
    CONSTRAINT topic_urls_quality_score_check CHECK (quality_score >= 0 AND quality_score <= 1),
    scraped_at TIMESTAMP WITH TIME ZONE,
    content_preview TEXT,
    title TEXT,
    word_count INTEGER,
    CONSTRAINT topic_urls_word_count_check CHECK (word_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(session_id, url)
);

-- Simple analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    CONSTRAINT fk_analysis_results_session FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
    analysis_id VARCHAR(50) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Core scoring results
    overall_score DECIMAL(5,4),
    CONSTRAINT analysis_results_overall_score_check CHECK (overall_score >= 0 AND overall_score <= 1),
    confidence_score DECIMAL(5,4),
    CONSTRAINT analysis_results_confidence_score_check CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Detailed results as JSON
    results_data JSONB DEFAULT '{}'::jsonb,
    processing_metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(session_id, analysis_id)
);

-- User activity tracking
CREATE TABLE IF NOT EXISTS user_activity (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSONB DEFAULT '{}'::jsonb,
    session_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);
CREATE INDEX IF NOT EXISTS idx_topics_created_at ON topics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_topic_urls_session_id ON topic_urls(session_id);
CREATE INDEX IF NOT EXISTS idx_topic_urls_status ON topic_urls(status);
CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);

-- Create trigger function for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to topics table
DROP TRIGGER IF EXISTS update_topics_updated_at ON topics;
CREATE TRIGGER update_topics_updated_at
    BEFORE UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant minimal necessary permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO validatus_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO validatus_app;
GRANT USAGE ON SCHEMA public TO validatus_app;

-- Insert sample data for testing
INSERT INTO topics (session_id, topic, description, user_id, search_queries, initial_urls) VALUES 
('sample_topic_001', 'Sample Market Analysis', 'This is a sample topic for testing the database setup', 'setup_user', ARRAY['market analysis', 'business intelligence'], ARRAY['https://example.com/market-research'])
ON CONFLICT (session_id) DO NOTHING;

INSERT INTO topic_urls (session_id, url, source, status) VALUES 
('sample_topic_001', 'https://example.com/market-research', 'initial', 'pending'),
('sample_topic_001', 'https://example.com/industry-trends', 'search', 'pending')
ON CONFLICT (session_id, url) DO NOTHING;
