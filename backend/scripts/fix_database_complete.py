#!/usr/bin/env python3
"""
Complete Database Fix Script for Validatus2
Fixes Cloud SQL connection and creates all required tables
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database_config import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fix_database_complete():
    """Complete database fix and setup"""
    
    logger.info("🚀 Starting Complete Database Fix for Validatus2")
    logger.info("=" * 60)
    
    db_manager = DatabaseManager()
    
    try:
        # Step 1: Test basic connection
        logger.info("Step 1: Testing database connection...")
        connection = await db_manager.get_connection()
        
        # Test basic query
        result = await connection.fetchval("SELECT version()")
        logger.info(f"✅ Database connected successfully: PostgreSQL {result[:30]}...")
        
        # Step 2: Create base schema
        logger.info("\nStep 2: Creating base database schema...")
        await create_base_schema(connection)
        
        # Step 3: Create additional tables for URL collection
        logger.info("\nStep 3: Creating URL collection tables...")
        await create_url_collection_schema(connection)
        
        # Step 4: Verify all tables exist
        logger.info("\nStep 4: Verifying database schema...")
        tables = await verify_database_schema(connection)
        
        # Step 5: Create test data
        logger.info("\nStep 5: Creating test data...")
        await create_test_data(connection)
        
        # Step 6: Test topic listing functionality
        logger.info("\nStep 6: Testing topic listing functionality...")
        await test_topic_listing(connection)
        
        logger.info("\n🎉 Complete Database Fix Completed Successfully!")
        logger.info(f"✅ Created {len(tables)} database tables")
        logger.info("✅ Topic listing functionality working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database fix failed: {e}")
        return False
    finally:
        await db_manager.close()

async def create_base_schema(connection):
    """Create base database schema"""
    
    base_schema = """
    -- Create extension if not exists
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Create topics table
    CREATE TABLE IF NOT EXISTS topics (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(50) UNIQUE NOT NULL,
        topic VARCHAR(500) NOT NULL,
        description TEXT,
        user_id VARCHAR(100) NOT NULL,
        analysis_type VARCHAR(50) DEFAULT 'comprehensive',
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB DEFAULT '{}'::jsonb,
        search_queries TEXT[],
        initial_urls TEXT[]
    );
    
    -- Create topic_urls table
    CREATE TABLE IF NOT EXISTS topic_urls (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(50) NOT NULL,
        url TEXT NOT NULL,
        url_hash VARCHAR(64),
        title TEXT,
        description TEXT,
        content TEXT,
        source VARCHAR(100) DEFAULT 'unknown',
        collection_method VARCHAR(100) DEFAULT 'manual',
        domain VARCHAR(255),
        relevance_score DECIMAL(3,2),
        quality_score DECIMAL(3,2),
        priority_level INTEGER DEFAULT 5,
        status VARCHAR(50) DEFAULT 'pending',
        scraped_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB DEFAULT '{}'::jsonb,
        
        -- Foreign key and constraints
        CONSTRAINT fk_topic_urls_session_id 
            FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
        CONSTRAINT unique_session_url_hash UNIQUE (session_id, url_hash),
        CONSTRAINT chk_relevance_score CHECK (relevance_score >= 0 AND relevance_score <= 1),
        CONSTRAINT chk_quality_score CHECK (quality_score >= 0 AND quality_score <= 1)
    );
    
    -- Create workflow_status table
    CREATE TABLE IF NOT EXISTS workflow_status (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(50) NOT NULL,
        stage VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        error_message TEXT,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        
        CONSTRAINT fk_workflow_status_session_id 
            FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
        CONSTRAINT unique_session_stage UNIQUE (session_id, stage)
    );
    
    -- Create basic indexes
    CREATE INDEX IF NOT EXISTS idx_topics_session_id ON topics(session_id);
    CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
    CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);
    CREATE INDEX IF NOT EXISTS idx_topic_urls_session_id ON topic_urls(session_id);
    CREATE INDEX IF NOT EXISTS idx_topic_urls_status ON topic_urls(status);
    CREATE INDEX IF NOT EXISTS idx_workflow_status_session_id ON workflow_status(session_id);
    """
    
    # Execute schema creation
    statements = [stmt.strip() for stmt in base_schema.split(';') if stmt.strip()]
    
    for i, statement in enumerate(statements, 1):
        try:
            await connection.execute(statement)
            logger.info(f"  [{i}/{len(statements)}] Executed successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"  [{i}/{len(statements)}] Skipped (already exists)")
            else:
                logger.error(f"  [{i}/{len(statements)}] Failed: {e}")
                raise

async def create_url_collection_schema(connection):
    """Create URL collection tables"""
    
    url_collection_schema = """
    -- Create URL collection campaigns table
    CREATE TABLE IF NOT EXISTS url_collection_campaigns (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(50) NOT NULL,
        campaign_name VARCHAR(200),
        collection_strategy VARCHAR(100) DEFAULT 'google_custom_search',
        search_queries TEXT[],
        max_urls INTEGER DEFAULT 20,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        progress_percentage DECIMAL(5,2) DEFAULT 0,
        urls_discovered INTEGER DEFAULT 0,
        urls_processed INTEGER DEFAULT 0,
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        error_message TEXT,
        configuration JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        
        CONSTRAINT fk_url_campaigns_session_id 
            FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
        CONSTRAINT chk_campaign_status 
            CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
    );
    
    -- Create search queries tracking table
    CREATE TABLE IF NOT EXISTS search_queries (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(50) NOT NULL,
        campaign_id INTEGER,
        query_text TEXT NOT NULL,
        total_results_found BIGINT DEFAULT 0,
        results_retrieved INTEGER DEFAULT 0,
        search_time_ms INTEGER DEFAULT 0,
        api_quota_cost INTEGER DEFAULT 1,
        executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        
        CONSTRAINT fk_search_queries_session_id 
            FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
        CONSTRAINT fk_search_queries_campaign_id 
            FOREIGN KEY (campaign_id) REFERENCES url_collection_campaigns(id) ON DELETE CASCADE
    );
    
    -- Add Google Custom Search columns to topic_urls
    ALTER TABLE topic_urls 
    ADD COLUMN IF NOT EXISTS search_rank INTEGER,
    ADD COLUMN IF NOT EXISTS search_query TEXT,
    ADD COLUMN IF NOT EXISTS snippet TEXT,
    ADD COLUMN IF NOT EXISTS formatted_url TEXT;
    
    -- Create indexes for URL collection
    CREATE INDEX IF NOT EXISTS idx_url_collection_campaigns_session_id 
        ON url_collection_campaigns(session_id);
    CREATE INDEX IF NOT EXISTS idx_url_collection_campaigns_status 
        ON url_collection_campaigns(status);
    CREATE INDEX IF NOT EXISTS idx_search_queries_session_id 
        ON search_queries(session_id);
    CREATE INDEX IF NOT EXISTS idx_search_queries_campaign_id 
        ON search_queries(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_topic_urls_search_rank 
        ON topic_urls(search_rank);
    """
    
    # Execute URL collection schema
    statements = [stmt.strip() for stmt in url_collection_schema.split(';') if stmt.strip()]
    
    for i, statement in enumerate(statements, 1):
        try:
            await connection.execute(statement)
            logger.info(f"  [{i}/{len(statements)}] URL collection table created")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                logger.info(f"  [{i}/{len(statements)}] Skipped (already exists)")
            else:
                logger.error(f"  [{i}/{len(statements)}] Failed: {e}")
                raise

async def verify_database_schema(connection):
    """Verify all required tables exist"""
    
    required_tables = [
        'topics', 'topic_urls', 'workflow_status', 
        'url_collection_campaigns', 'search_queries'
    ]
    
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
    """
    
    tables = await connection.fetch(query)
    existing_tables = [row['table_name'] for row in tables]
    
    logger.info("  Database Tables:")
    for table in existing_tables:
        status = "✅" if table in required_tables else "ℹ️"
        logger.info(f"    {status} {table}")
    
    missing_tables = set(required_tables) - set(existing_tables)
    if missing_tables:
        raise Exception(f"Missing required tables: {missing_tables}")
    
    return existing_tables

async def create_test_data(connection):
    """Create test data for verification"""
    
    test_data_sql = """
    -- Insert test topic
    INSERT INTO topics (session_id, topic, description, user_id, status, search_queries, initial_urls)
    VALUES (
        'test-session-db-fix-001', 
        'Database Connection Test Topic', 
        'This topic was created during database fix verification',
        'db-fix-user',
        'CREATED',
        ARRAY['database test', 'connection verification'],
        ARRAY['https://example.com/test']
    ) ON CONFLICT (session_id) DO UPDATE SET
        updated_at = NOW();
    
    -- Insert test URL
    INSERT INTO topic_urls (session_id, url, url_hash, title, description, source, status)
    VALUES (
        'test-session-db-fix-001',
        'https://example.com/test',
        'test-url-hash-001',
        'Database Test URL',
        'Test URL created during database fix',
        'manual',
        'pending'
    ) ON CONFLICT (session_id, url_hash) DO UPDATE SET
        updated_at = NOW();
    
    -- Insert workflow status
    INSERT INTO workflow_status (session_id, stage, status)
    VALUES (
        'test-session-db-fix-001',
        'URL_COLLECTION',
        'completed'
    ) ON CONFLICT (session_id, stage) DO UPDATE SET
        status = 'completed',
        completed_at = NOW();
    """
    
    statements = [stmt.strip() for stmt in test_data_sql.split(';') if stmt.strip()]
    
    for statement in statements:
        try:
            await connection.execute(statement)
            logger.info("  ✅ Test data created successfully")
        except Exception as e:
            logger.error(f"  ❌ Test data creation failed: {e}")

async def test_topic_listing(connection):
    """Test topic listing functionality"""
    
    # Test basic topic retrieval
    topics_query = """
    SELECT t.session_id, t.topic, t.user_id, t.status, t.created_at,
           COUNT(tu.id) as url_count
    FROM topics t
    LEFT JOIN topic_urls tu ON t.session_id = tu.session_id
    GROUP BY t.session_id, t.topic, t.user_id, t.status, t.created_at
    ORDER BY t.created_at DESC
    """
    
    topics = await connection.fetch(topics_query)
    
    logger.info(f"  📋 Found {len(topics)} topics in database:")
    for topic in topics:
        logger.info(f"    • {topic['topic']} (URLs: {topic['url_count']})")
    
    if len(topics) == 0:
        raise Exception("No topics found in database - topic listing test failed")
    
    logger.info("  ✅ Topic listing functionality verified")

if __name__ == "__main__":
    success = asyncio.run(fix_database_complete())
    sys.exit(0 if success else 1)
