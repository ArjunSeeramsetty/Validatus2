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
        
        -- ===== RESULTS PERSISTENCE TABLES =====
        
        -- Create computed_factors table for storing factor calculations
        CREATE TABLE IF NOT EXISTS computed_factors (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            segment VARCHAR(50) NOT NULL,
            factor_id VARCHAR(10) NOT NULL,
            factor_value DECIMAL(10,6) NOT NULL,
            confidence DECIMAL(10,6) NOT NULL,
            formula_applied TEXT,
            calculation_metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_session_factor UNIQUE(session_id, factor_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_factors_session ON computed_factors(session_id);
        CREATE INDEX IF NOT EXISTS idx_factors_segment ON computed_factors(session_id, segment);
        
        -- Create pattern_matches table
        CREATE TABLE IF NOT EXISTS pattern_matches (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            segment VARCHAR(50) NOT NULL,
            pattern_id VARCHAR(10) NOT NULL,
            pattern_name VARCHAR(255) NOT NULL,
            pattern_type VARCHAR(50) NOT NULL,
            confidence DECIMAL(10,6) NOT NULL,
            match_score DECIMAL(10,6) NOT NULL,
            strategic_response TEXT,
            effect_size_hints TEXT,
            probability_range JSONB,
            factors_triggered JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_patterns_session ON pattern_matches(session_id);
        CREATE INDEX IF NOT EXISTS idx_patterns_segment ON pattern_matches(session_id, segment);
        
        -- Create monte_carlo_scenarios table
        CREATE TABLE IF NOT EXISTS monte_carlo_scenarios (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            segment VARCHAR(50) NOT NULL,
            scenario_id VARCHAR(100) NOT NULL,
            pattern_id VARCHAR(10) NOT NULL,
            pattern_name VARCHAR(255) NOT NULL,
            strategic_response TEXT,
            kpi_results JSONB NOT NULL,
            probability_success DECIMAL(10,6) NOT NULL,
            confidence_interval JSONB NOT NULL,
            iterations INTEGER DEFAULT 1000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_session_scenario UNIQUE(session_id, scenario_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_scenarios_session ON monte_carlo_scenarios(session_id);
        CREATE INDEX IF NOT EXISTS idx_scenarios_segment ON monte_carlo_scenarios(session_id, segment);
        
        -- Create consumer_personas table
        CREATE TABLE IF NOT EXISTS consumer_personas (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            persona_name VARCHAR(255) NOT NULL,
            age VARCHAR(50),
            demographics JSONB,
            psychographics JSONB,
            pain_points JSONB,
            goals JSONB,
            buying_behavior JSONB,
            market_share DECIMAL(10,6),
            value_tier VARCHAR(50),
            key_messaging JSONB,
            confidence DECIMAL(10,6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_personas_session ON consumer_personas(session_id);
        
        -- Create segment_rich_content table
        CREATE TABLE IF NOT EXISTS segment_rich_content (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            segment VARCHAR(50) NOT NULL,
            content_type VARCHAR(100) NOT NULL,
            content_data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_session_segment_content UNIQUE(session_id, segment, content_type)
        );
        
        CREATE INDEX IF NOT EXISTS idx_rich_content_session ON segment_rich_content(session_id);
        
        -- Create results_generation_status table
        CREATE TABLE IF NOT EXISTS results_generation_status (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL UNIQUE,
            topic VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            current_stage VARCHAR(100),
            progress_percentage INTEGER DEFAULT 0,
            total_segments INTEGER DEFAULT 5,
            completed_segments INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_results_status ON results_generation_status(session_id, status);
        
        -- ===== URL COLLECTION TABLES =====
        
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
        
        if len(tables) >= 8:  # 2 URL collection + 6 results persistence tables
            print("✅ All required tables created successfully!")
        else:
            print(f"⚠️ Some tables may not have been created properly (found {len(tables)} tables)")
        
        # Close connection
        await conn.close()
        print("🔌 Database connection closed")
        
        return {
            "status": "success",
            "message": "Database migration completed successfully",
            "details": "Created URL collection tables and results persistence tables (factors, patterns, scenarios, personas, content, status)",
            "tables_created": [table['table_name'] for table in tables],
            "total_tables": len(tables)
        }
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {str(e)}"
        )
