-- Initial schema for Cloud SQL PostgreSQL
-- This will be applied during database initialization

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Topics table
CREATE TABLE topics (
    session_id VARCHAR(50) PRIMARY KEY,
    topic VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
    analysis_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    search_queries TEXT[],
    initial_urls TEXT[],
    
    -- Add constraints
    CONSTRAINT chk_topic_status CHECK (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'ARCHIVED')),
    CONSTRAINT chk_analysis_type CHECK (analysis_type IN ('standard', 'comprehensive'))
);

-- URLs table for tracking URL collection and processing
CREATE TABLE topic_urls (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL REFERENCES topics(session_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    source VARCHAR(100) NOT NULL DEFAULT 'unknown', -- 'initial', 'search', 'discovered'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing' 'scraped', 'failed'
    quality_score DECIMAL(3,2),
    scraped_at TIMESTAMP WITH TIME ZONE,
    content_storage_path TEXT, -- GCS path for actual content
    content_hash VARCHAR(64), -- SHA-256 hash for deduplication
    title TEXT,
    word_count INTEGER,
    processing_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure URL uniqueness per session
    UNIQUE(session_id, url),
    
    -- Add constraints
    CONSTRAINT chk_url_status CHECK (status IN ('pending', 'processing', 'scraped', 'failed', 'skipped')),
    CONSTRAINT chk_quality_score CHECK (quality_score >= 0 AND quality_score <= 1)
);

-- Workflow status tracking
CREATE TABLE workflow_status (
    session_id VARCHAR(50) PRIMARY KEY REFERENCES topics(session_id) ON DELETE CASCADE,
    current_stage VARCHAR(50) NOT NULL,
    stages_completed TEXT[] DEFAULT '{}',
    stage_progress JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Add constraints
    CONSTRAINT chk_current_stage CHECK (current_stage IN (
        'CREATED', 'URL_COLLECTION', 'URL_SCRAPING', 'CONTENT_PROCESSING', 
        'VECTOR_CREATION', 'ANALYSIS', 'COMPLETED', 'FAILED'
    ))
);

-- Vector embeddings metadata (actual vectors stored in Vertex AI)
CREATE TABLE vector_embeddings (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL REFERENCES topics(session_id) ON DELETE CASCADE,
    url_id INTEGER REFERENCES topic_urls(id) ON DELETE CASCADE,
    chunk_id VARCHAR(100) NOT NULL,
    content_preview TEXT, -- First 500 chars of chunk
    chunk_index INTEGER NOT NULL,
    vertex_ai_index_id TEXT,
    vertex_ai_endpoint_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure uniqueness
    UNIQUE(session_id, chunk_id)
);

-- Analysis sessions and results metadata (detailed results in Spanner)
CREATE TABLE analysis_sessions (
    analysis_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL REFERENCES topics(session_id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    spanner_result_id TEXT, -- Reference to Cloud Spanner record
    summary_results JSONB DEFAULT '{}'::jsonb,
    
    -- Add constraints
    CONSTRAINT chk_analysis_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

-- Performance indexes
CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_topics_status ON topics(status);
CREATE INDEX idx_topics_created_at ON topics(created_at DESC);
CREATE INDEX idx_topics_user_status ON topics(user_id, status);

CREATE INDEX idx_topic_urls_session_id ON topic_urls(session_id);
CREATE INDEX idx_topic_urls_status ON topic_urls(status);
CREATE INDEX idx_topic_urls_session_status ON topic_urls(session_id, status);
CREATE INDEX idx_topic_urls_content_hash ON topic_urls(content_hash) WHERE content_hash IS NOT NULL;

CREATE INDEX idx_workflow_status_stage ON workflow_status(current_stage);
CREATE INDEX idx_workflow_status_updated ON workflow_status(updated_at DESC);

CREATE INDEX idx_vector_embeddings_session ON vector_embeddings(session_id);
CREATE INDEX idx_vector_embeddings_url ON vector_embeddings(url_id);

CREATE INDEX idx_analysis_sessions_session_id ON analysis_sessions(session_id);
CREATE INDEX idx_analysis_sessions_status ON analysis_sessions(status);

-- Full-text search indexes
CREATE INDEX idx_topics_search ON topics USING GIN (to_tsvector('english', topic || ' ' || description));
CREATE INDEX idx_topic_urls_title_search ON topic_urls USING GIN (to_tsvector('english', COALESCE(title, '')));

-- Trigger for updating updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_topic_urls_updated_at BEFORE UPDATE ON topic_urls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_status_updated_at BEFORE UPDATE ON workflow_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
