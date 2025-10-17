# backend/scripts/create_results_persistence_tables.py

"""
Create results persistence tables for data-driven analysis
Run this script to set up the database schema for Cloud SQL persistence
"""

import asyncio
import logging
from sqlalchemy import text
from app.core.database_config import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_results_persistence_tables():
    """Create all tables for results persistence"""
    
    logger.info("🚀 Starting results persistence tables creation...")
    
    try:
        # Get database connection
        async with db_manager.get_async_session() as session:
            
            # Read SQL migration file
            with open('backend/database/migrations/add_results_persistence_tables.sql', 'r') as f:
                sql_content = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            # Execute each statement
            for i, statement in enumerate(statements, 1):
                if statement:
                    logger.info(f"Executing statement {i}/{len(statements)}...")
                    try:
                        await session.execute(text(statement))
                        await session.commit()
                        logger.info(f"✅ Statement {i} executed successfully")
                    except Exception as e:
                        logger.warning(f"⚠️ Statement {i} failed (may already exist): {e}")
                        await session.rollback()
                        # Continue with other statements
            
            logger.info("✅ All results persistence tables created successfully!")
            
            # Verify tables exist
            await verify_tables_exist(session)
            
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

async def verify_tables_exist(session):
    """Verify that all required tables exist"""
    
    required_tables = [
        'computed_factors',
        'pattern_matches', 
        'monte_carlo_scenarios',
        'consumer_personas',
        'segment_rich_content',
        'results_generation_status'
    ]
    
    logger.info("🔍 Verifying tables exist...")
    
    for table in required_tables:
        try:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            logger.info(f"✅ Table '{table}' exists (rows: {count})")
        except Exception as e:
            logger.error(f"❌ Table '{table}' not found: {e}")
            raise

async def main():
    """Main function"""
    try:
        await create_results_persistence_tables()
        logger.info("🎉 Results persistence tables setup complete!")
        logger.info("📊 Ready for data-driven analysis with Cloud SQL persistence")
    except Exception as e:
        logger.error(f"💥 Setup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
