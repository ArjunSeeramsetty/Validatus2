# backend/app/api/v3/database_migration.py

"""
Database migration API endpoint
Run migrations from Cloud Run with Cloud SQL access
"""

from fastapi import APIRouter, HTTPException
import logging
from sqlalchemy import text
from app.core.database_session import db_session_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/run-results-persistence-migration")
async def run_results_persistence_migration():
    """
    Create results persistence tables in Cloud SQL
    Call this endpoint to set up the database schema
    """
    
    logger.info("🚀 Starting results persistence migration...")
    
    try:
        # Get a synchronous session
        db = db_session_manager.get_session()
        
        tables_created = []
        tables_existed = []
        errors = []
        
        # Define all table creation statements
        tables = [
            ("computed_factors", """
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
                )
            """),
            ("pattern_matches", """
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
                )
            """),
            ("monte_carlo_scenarios", """
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
                )
            """),
            ("consumer_personas", """
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
                )
            """),
            ("segment_rich_content", """
                CREATE TABLE IF NOT EXISTS segment_rich_content (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    topic VARCHAR(255) NOT NULL,
                    segment VARCHAR(50) NOT NULL,
                    content_type VARCHAR(100) NOT NULL,
                    content_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_session_segment_content UNIQUE(session_id, segment, content_type)
                )
            """),
            ("results_generation_status", """
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
                )
            """)
        ]
        
        # Create tables
        for table_name, create_sql in tables:
            try:
                db.execute(text(create_sql))
                db.commit()
                tables_created.append(table_name)
                logger.info(f"✅ Table '{table_name}' created/verified")
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg:
                    tables_existed.append(table_name)
                    logger.info(f"ℹ️ Table '{table_name}' already exists")
                else:
                    errors.append(f"{table_name}: {error_msg}")
                    logger.error(f"❌ Error creating table '{table_name}': {e}")
                db.rollback()
        
        # Create indexes
        indexes = [
            ("idx_factors_session", "CREATE INDEX IF NOT EXISTS idx_factors_session ON computed_factors(session_id)"),
            ("idx_factors_segment", "CREATE INDEX IF NOT EXISTS idx_factors_segment ON computed_factors(session_id, segment)"),
            ("idx_patterns_session", "CREATE INDEX IF NOT EXISTS idx_patterns_session ON pattern_matches(session_id)"),
            ("idx_patterns_segment", "CREATE INDEX IF NOT EXISTS idx_patterns_segment ON pattern_matches(session_id, segment)"),
            ("idx_scenarios_session", "CREATE INDEX IF NOT EXISTS idx_scenarios_session ON monte_carlo_scenarios(session_id)"),
            ("idx_scenarios_segment", "CREATE INDEX IF NOT EXISTS idx_scenarios_segment ON monte_carlo_scenarios(session_id, segment)"),
            ("idx_personas_session", "CREATE INDEX IF NOT EXISTS idx_personas_session ON consumer_personas(session_id)"),
            ("idx_rich_content_session", "CREATE INDEX IF NOT EXISTS idx_rich_content_session ON segment_rich_content(session_id)"),
            ("idx_results_status", "CREATE INDEX IF NOT EXISTS idx_results_status ON results_generation_status(session_id, status)")
        ]
        
        indexes_created = []
        for index_name, index_sql in indexes:
            try:
                db.execute(text(index_sql))
                db.commit()
                indexes_created.append(index_name)
                logger.info(f"✅ Index '{index_name}' created/verified")
            except Exception as e:
                logger.warning(f"⚠️ Index '{index_name}' creation failed: {e}")
                db.rollback()
        
        db.close()
        
        logger.info("🎉 Migration completed!")
        
        return {
            "status": "success",
            "message": "Results persistence tables migration completed",
            "tables_created": tables_created,
            "tables_existed": tables_existed,
            "indexes_created": indexes_created,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@router.get("/verify-tables")
async def verify_results_persistence_tables():
    """
    Verify that all results persistence tables exist
    """
    
    logger.info("🔍 Verifying results persistence tables...")
    
    try:
        db = db_session_manager.get_session()
        
        required_tables = [
            'computed_factors',
            'pattern_matches',
            'monte_carlo_scenarios',
            'consumer_personas',
            'segment_rich_content',
            'results_generation_status'
        ]
        
        table_status = {}
        
        for table in required_tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                table_status[table] = {
                    "exists": True,
                    "row_count": count
                }
                logger.info(f"✅ Table '{table}' exists with {count} rows")
            except Exception as e:
                table_status[table] = {
                    "exists": False,
                    "error": str(e)
                }
                logger.error(f"❌ Table '{table}' not found: {e}")
        
        db.close()
        
        all_exist = all(status["exists"] for status in table_status.values())
        
        return {
            "status": "success" if all_exist else "incomplete",
            "message": "All tables exist" if all_exist else "Some tables are missing",
            "tables": table_status,
            "all_tables_exist": all_exist
        }
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
