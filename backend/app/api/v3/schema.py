"""
Database Schema API - For testing and setup
"""
import asyncio
import logging
from fastapi import APIRouter, HTTPException
from ...core.database_config import db_manager
import asyncpg

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create-schema")
async def create_database_schema():
    """Create database schema for testing"""
    try:
        connection = await db_manager.get_connection()
        
        # Test basic connection first
        await connection.fetchval("SELECT 1")
        logger.info("✅ Database connection successful")
        
        # Create basic schema
        schema_sql = """
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
            initial_urls TEXT[],
            CONSTRAINT chk_analysis_type CHECK (analysis_type IN ('standard', 'comprehensive', 'quick', 'deep')),
            CONSTRAINT chk_status CHECK (status IN ('draft', 'pending', 'created', 'in_progress', 'completed', 'failed', 'archived'))
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
            status VARCHAR(50) DEFAULT 'pending',
            scraped_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'::jsonb,
            
            CONSTRAINT fk_topic_urls_session_id 
                FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
            CONSTRAINT chk_url_status CHECK (status IN ('pending', 'processing', 'scraped', 'completed', 'failed', 'skipped'))
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
            CONSTRAINT unique_session_stage UNIQUE (session_id, stage),
            CONSTRAINT chk_workflow_stage CHECK (stage IN ('initialization', 'url_collection', 'scraping', 'analysis', 'completion')),
            CONSTRAINT chk_workflow_status CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'))
        );
        
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
            CONSTRAINT chk_campaign_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
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
        
        -- Add missing columns to existing topics table
        ALTER TABLE topics ADD COLUMN IF NOT EXISTS search_queries TEXT[];
        ALTER TABLE topics ADD COLUMN IF NOT EXISTS initial_urls TEXT[];
        
        -- Add missing columns to topic_urls table for enhanced URL collection
        ALTER TABLE topic_urls ADD COLUMN IF NOT EXISTS collection_method VARCHAR(100);
        ALTER TABLE topic_urls ADD COLUMN IF NOT EXISTS domain VARCHAR(255);
        ALTER TABLE topic_urls ADD COLUMN IF NOT EXISTS relevance_score DECIMAL(3,2);
        ALTER TABLE topic_urls ADD COLUMN IF NOT EXISTS quality_score DECIMAL(3,2);
        ALTER TABLE topic_urls ADD COLUMN IF NOT EXISTS priority_level INTEGER DEFAULT 5;
        ALTER TABLE topic_urls ADD COLUMN IF NOT EXISTS search_query TEXT;
        
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_topics_session_id ON topics(session_id);
        CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
        CREATE INDEX IF NOT EXISTS idx_topic_urls_session_id ON topic_urls(session_id);
        CREATE INDEX IF NOT EXISTS idx_workflow_status_session_id ON workflow_status(session_id);
        CREATE INDEX IF NOT EXISTS idx_url_campaigns_session_id ON url_collection_campaigns(session_id);
        CREATE INDEX IF NOT EXISTS idx_url_campaigns_status ON url_collection_campaigns(status);
        CREATE INDEX IF NOT EXISTS idx_search_queries_session_id ON search_queries(session_id);
        CREATE INDEX IF NOT EXISTS idx_search_queries_campaign_id ON search_queries(campaign_id);
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_topics_session_id ON topics(session_id);
        CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
        CREATE INDEX IF NOT EXISTS idx_topic_urls_session_id ON topic_urls(session_id);
        CREATE INDEX IF NOT EXISTS idx_workflow_status_session_id ON workflow_status(session_id);
        CREATE INDEX IF NOT EXISTS idx_url_campaigns_session_id ON url_collection_campaigns(session_id);
        CREATE INDEX IF NOT EXISTS idx_url_campaigns_status ON url_collection_campaigns(status);
        CREATE INDEX IF NOT EXISTS idx_search_queries_session_id ON search_queries(session_id);
        CREATE INDEX IF NOT EXISTS idx_search_queries_campaign_id ON search_queries(campaign_id);
        """
        
        # Execute schema creation - execute entire block to avoid splitting issues
        try:
            await connection.execute(schema_sql)
            logger.info("✅ Schema created successfully (executed as single transaction)")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info("✅ Schema already exists, skipping creation")
            else:
                logger.error(f"Schema creation failed: {e}")
                raise
        
        # Create trigger function separately (handles dollar-quoted strings properly)
        trigger_sql = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        try:
            await connection.execute(trigger_sql)
            logger.info("✅ Trigger function created")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info("✅ Trigger function already exists")
            else:
                logger.warning(f"Trigger function creation warning: {e}")
        
        # Create trigger
        trigger_create_sql = """
        DROP TRIGGER IF EXISTS update_topics_updated_at ON topics;
        CREATE TRIGGER update_topics_updated_at 
        BEFORE UPDATE ON topics
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        try:
            await connection.execute(trigger_create_sql)
            logger.info("✅ Trigger created")
        except Exception as e:
            logger.warning(f"Trigger creation warning: {e}")
        
        # Add unique constraint to topic_urls table (separate to handle errors gracefully)
        try:
            await connection.execute(
                "ALTER TABLE topic_urls ADD CONSTRAINT unique_session_url_hash UNIQUE (session_id, url_hash)"
            )
            logger.info("  ✅ Added unique constraint to topic_urls")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info("  ℹ️  Unique constraint already exists on topic_urls")
            else:
                logger.warning(f"  ⚠️  Could not add unique constraint: {e}")
        
        # Verify schema by checking table existence (no test data insertion)
        try:
            result = await connection.fetch("""
                SELECT COUNT(*) as count FROM topics LIMIT 1
            """)
            logger.info(f"✅ Topics table verified: {result[0]['count']} existing records")
        except Exception as e:
            logger.error(f"❌ Topics table verification failed: {e}")
            raise
        
        return {
            "status": "success",
            "message": "Database schema created successfully",
            "tables_created": 5,  # topics, topic_urls, workflow_status, url_collection_campaigns, search_queries
            "schema_verified": True
        }
        
    except Exception as e:
        logger.error(f"Schema creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Schema creation failed: {str(e)}")

@router.get("/test-connection")
async def test_database_connection():
    """Test database connection"""
    try:
        connection = await db_manager.get_connection()
        version = await connection.fetchval("SELECT version()")
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_version": version[:50] + "..." if len(version) > 50 else version
        }
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.get("/list-tables")
async def list_database_tables():
    """List all tables in the database"""
    try:
        connection = await db_manager.get_connection()
        
        query = """
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        
        tables = await connection.fetch(query)
        
        return {
            "status": "success",
            "tables": [{"name": row["table_name"], "type": row["table_type"]} for row in tables]
        }
        
    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {str(e)}")
