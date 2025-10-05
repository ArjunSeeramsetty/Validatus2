#!/usr/bin/env python3
"""
Simple database schema setup for Validatus
"""
import asyncio
import asyncpg
import os

async def setup_database():
    # Database connection details
    connection_string = "postgresql://validatus_app:Validatus2024!@35.232.190.254:5432/validatusdb"
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = await asyncpg.connect(connection_string)
        print("Connected to database successfully")
        
        # Create schema
        schema_sql = """
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
            analysis_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
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
            url TEXT NOT NULL,
            source VARCHAR(100) NOT NULL DEFAULT 'unknown',
            status VARCHAR(50) DEFAULT 'pending',
            quality_score DECIMAL(3,2),
            scraped_at TIMESTAMP WITH TIME ZONE,
            content_preview TEXT,
            title TEXT,
            word_count INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            UNIQUE(session_id, url)
        );

        -- Simple analysis results table
        CREATE TABLE IF NOT EXISTS analysis_results (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(50) NOT NULL,
            analysis_id VARCHAR(50) NOT NULL,
            analysis_type VARCHAR(50) NOT NULL,
            user_id VARCHAR(100) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            -- Core scoring results
            overall_score DECIMAL(5,4),
            confidence_score DECIMAL(5,4),
            
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

        -- Grant permissions to application user
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO validatus_app;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO validatus_app;
        GRANT USAGE ON SCHEMA public TO validatus_app;

        -- Insert sample data for testing
        INSERT INTO topics (session_id, topic, description, user_id, search_queries, initial_urls) VALUES 
        ('sample_topic_001', 'Sample Market Analysis', 'This is a sample topic for testing the database setup', 'setup_user', ARRAY['market analysis', 'business intelligence'], ARRAY['https://example.com/market-research'])
        ON CONFLICT (session_id) DO NOTHING;

        INSERT INTO topic_urls (session_id, url, source, status) VALUES 
        ('sample_topic_001', 'https://example.com/market-research', 'initial', 'pending'),
        ('sample_topic_001', 'https://example.com/industry-trends', 'search', 'pending')
        ON CONFLICT (session_id, url) DO NOTHING;
        """
        
        print("Creating database schema...")
        await conn.execute(schema_sql)
        print("Database schema created successfully")
        
        # Test the setup
        print("Testing database setup...")
        result = await conn.fetchval("SELECT COUNT(*) FROM topics")
        print(f"Found {result} topics in database")
        
        # Close connection
        await conn.close()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_database())
