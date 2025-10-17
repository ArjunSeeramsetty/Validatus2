# backend/run_migration.py

"""
Simple migration script to create results persistence tables
Run this from the backend directory
"""

import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database_config import db_manager
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    """Create results persistence tables"""
    
    logger.info("🚀 Creating results persistence tables...")
    
    try:
        async with db_manager.get_async_session() as session:
            
            # Create tables one by one
            tables = [
                """
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
                """,
                """
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
                """,
                """
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
                """,
                """
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
                """,
                """
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
                """,
                """
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
                """
            ]
            
            for i, table_sql in enumerate(tables, 1):
                logger.info(f"Creating table {i}/6...")
                try:
                    await session.execute(text(table_sql))
                    await session.commit()
                    logger.info(f"✅ Table {i} created successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Table {i} creation failed (may already exist): {e}")
                    await session.rollback()
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_factors_session ON computed_factors(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_factors_segment ON computed_factors(session_id, segment)",
                "CREATE INDEX IF NOT EXISTS idx_patterns_session ON pattern_matches(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_patterns_segment ON pattern_matches(session_id, segment)",
                "CREATE INDEX IF NOT EXISTS idx_scenarios_session ON monte_carlo_scenarios(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_scenarios_segment ON monte_carlo_scenarios(session_id, segment)",
                "CREATE INDEX IF NOT EXISTS idx_personas_session ON consumer_personas(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_rich_content_session ON segment_rich_content(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_results_status ON results_generation_status(session_id, status)"
            ]
            
            for i, index_sql in enumerate(indexes, 1):
                logger.info(f"Creating index {i}/{len(indexes)}...")
                try:
                    await session.execute(text(index_sql))
                    await session.commit()
                    logger.info(f"✅ Index {i} created successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Index {i} creation failed: {e}")
                    await session.rollback()
            
            logger.info("🎉 Database migration completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

async def main():
    """Main function"""
    try:
        await create_tables()
        logger.info("✅ Results persistence tables ready!")
        return True
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)