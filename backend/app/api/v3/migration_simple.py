"""
Simple Database Migration API Endpoints
"""

from fastapi import APIRouter, HTTPException
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.gcp_persistence_config import get_gcp_persistence_settings

router = APIRouter(prefix="/migration", tags=["migration"])

@router.post("/run")
async def run_database_migration():
    """
    Run database migration to create missing tables for Google Custom Search integration
    """
    try:
        print("🗄️ Starting database migration for Google Custom Search integration...")
        
        # Get database configuration
        settings = get_gcp_persistence_settings()
        
        # Build connection string
        if settings.local_development_mode:
            # Local development - use SQLite
            print("⚠️ Running in local development mode - skipping Cloud SQL migration")
            return {
                "status": "success",
                "message": "Local development mode - no migration needed",
                "details": "SQLite is used in local development"
            }
        
        # Cloud SQL connection
        password = settings.get_secret("cloud-sql-password")
        connection_string = f"postgresql://{settings.cloud_sql_user}:{password}@{settings.cloud_sql_connection_name.split(':')[2]}/{settings.cloud_sql_database}"
        
        print(f"🔌 Connecting to Cloud SQL database...")
        print(f"Database: {settings.cloud_sql_database}")
        print(f"Instance: {settings.cloud_sql_connection_name}")
        
        # Connect to database
        conn = await asyncpg.connect(connection_string)
        
        print("✅ Connected to database successfully!")
        
        # Create the missing tables directly
        migration_sql = """
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
        
        -- Grant permissions to validatus_app user
        GRANT SELECT, INSERT, UPDATE, DELETE ON url_collection_campaigns TO validatus_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON search_queries TO validatus_app;
        GRANT USAGE, SELECT ON SEQUENCE url_collection_campaigns_id_seq TO validatus_app;
        GRANT USAGE, SELECT ON SEQUENCE search_queries_id_seq TO validatus_app;
        """
        
        print("🚀 Executing migration SQL...")
        
        # Execute the migration SQL
        await conn.execute(migration_sql)
        
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        print("🔍 Verifying tables were created...")
        
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('url_collection_campaigns', 'search_queries')
        ORDER BY table_name;
        """
        
        tables = await conn.fetch(tables_query)
        
        print("📋 Created tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        if len(tables) == 2:
            print("✅ All required tables created successfully!")
        else:
            print("⚠️ Some tables may not have been created properly")
        
        # Close connection
        await conn.close()
        print("🔌 Database connection closed")
        
        return {
            "status": "success",
            "message": "Database migration completed successfully",
            "details": "Created url_collection_campaigns and search_queries tables",
            "tables_created": [table['table_name'] for table in tables]
        }
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {str(e)}"
        )
