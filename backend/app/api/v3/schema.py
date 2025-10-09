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
        
        -- 🆕 NEW: Create scraped_content table for content management
        CREATE TABLE IF NOT EXISTS scraped_content (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(50) NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            content TEXT,
            scraped_at TIMESTAMP WITH TIME ZONE NOT NULL,
            processing_status VARCHAR(50) DEFAULT 'pending',
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT fk_scraped_content_session_id 
                FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE,
            CONSTRAINT unique_session_url UNIQUE (session_id, url),
            CONSTRAINT chk_scraping_status CHECK (processing_status IN ('pending', 'processing', 'processed', 'failed'))
        );
        
        -- 🆕 NEW: Create analysis_scores table for scoring results  
        CREATE TABLE IF NOT EXISTS analysis_scores (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(50) NOT NULL,
            analysis_type VARCHAR(100) NOT NULL,
            score DECIMAL(5,3),
            confidence DECIMAL(5,3),
            analysis_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'::jsonb,
            
            CONSTRAINT fk_analysis_scores_session_id 
                FOREIGN KEY (session_id) REFERENCES topics(session_id) ON DELETE CASCADE
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
            "tables_created": 7,  # topics, topic_urls, workflow_status, url_collection_campaigns, search_queries, scraped_content, analysis_scores
            "schema_verified": True,
            "new_tables": ["scraped_content", "analysis_scores"]  # 🆕 NEW tables added
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

@router.get("/check-google-credentials")
async def check_google_credentials():
    """Check if Google Custom Search credentials are configured (for debugging)"""
    try:
        import os
        from ...core.gcp_persistence_config import get_gcp_persistence_settings
        
        settings = get_gcp_persistence_settings()
        
        # Check environment variables
        env_api_key = os.getenv("GOOGLE_CSE_API_KEY")
        env_cse_id = os.getenv("GOOGLE_CSE_ID")
        
        # Check Pydantic settings
        pydantic_api_key = settings.google_cse_api_key
        pydantic_cse_id = settings.google_cse_id
        
        # Try to get via the secure methods
        try:
            secure_api_key = settings.get_secure_api_key()
            api_key_status = "✅ Retrieved" if secure_api_key else "❌ Empty"
            api_key_length = len(secure_api_key) if secure_api_key else 0
        except Exception as e:
            api_key_status = f"❌ Error: {str(e)}"
            api_key_length = 0
        
        try:
            secure_cse_id = settings.get_secure_cse_id()
            cse_id_status = "✅ Retrieved" if secure_cse_id else "❌ Empty"
            cse_id_value = secure_cse_id[:20] + "..." if secure_cse_id and len(secure_cse_id) > 20 else secure_cse_id
        except Exception as e:
            cse_id_status = f"❌ Error: {str(e)}"
            cse_id_value = None
        
        return {
            "status": "success",
            "environment_variables": {
                "GOOGLE_CSE_API_KEY": "Present" if env_api_key else "Missing",
                "GOOGLE_CSE_API_KEY_length": len(env_api_key) if env_api_key else 0,
                "GOOGLE_CSE_ID": "Present" if env_cse_id else "Missing",
                "GOOGLE_CSE_ID_value": env_cse_id[:20] + "..." if env_cse_id and len(env_cse_id) > 20 else env_cse_id
            },
            "pydantic_settings": {
                "google_cse_api_key": "Present" if pydantic_api_key else "Missing",
                "google_cse_api_key_length": len(pydantic_api_key) if pydantic_api_key else 0,
                "google_cse_id": "Present" if pydantic_cse_id else "Missing",
                "google_cse_id_value": pydantic_cse_id[:20] + "..." if pydantic_cse_id and len(pydantic_cse_id) > 20 else pydantic_cse_id
            },
            "secure_retrieval": {
                "api_key_status": api_key_status,
                "api_key_length": api_key_length,
                "cse_id_status": cse_id_status,
                "cse_id_value": cse_id_value
            },
            "local_development_mode": settings.local_development_mode
        }
        
    except Exception as e:
        logger.error(f"Failed to check Google credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check credentials: {str(e)}")

@router.post("/create-v2-schema")
async def create_v2_database_schema():
    """Create v2.0 database schema for 5-segment, 28-factor, 210-layer analysis"""
    try:
        connection = await db_manager.get_connection()
        
        # Read and execute v2 schema SQL
        from pathlib import Path
        schema_path = Path(__file__).parent.parent.parent / "database" / "v2_scoring_schema.sql"
        
        if not schema_path.exists():
            raise HTTPException(status_code=500, detail="v2 schema file not found")
        
        with open(schema_path, 'r') as f:
            v2_schema_sql = f.read()
        
        # Execute as single transaction
        await connection.execute(v2_schema_sql)
        
        # Verify tables created
        tables_query = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' 
        AND table_name IN ('segments', 'factors', 'layers', 'layer_scores', 
                          'factor_calculations', 'segment_analysis', 'v2_analysis_results')
        ORDER BY table_name
        """
        created_tables = await connection.fetch(tables_query)
        
        return {
            "status": "success",
            "message": "v2.0 database schema created successfully",
            "tables_created": len(created_tables),
            "v2_tables": [row['table_name'] for row in created_tables],
            "configuration": {
                "segments": 5,
                "factors": 28,
                "layers": 210
            }
        }
        
    except Exception as e:
        logger.error(f"v2 schema creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"v2 schema creation failed: {str(e)}")
