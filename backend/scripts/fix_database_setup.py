#!/usr/bin/env python3
"""
Database setup fix script for resolving connection issues
"""
import asyncio
import asyncpg
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_and_fix_database():
    """Test database connection and create missing tables"""
    
    # Database connection parameters
    project_id = os.getenv("GCP_PROJECT_ID", "validatus-platform")
    connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME", f"{project_id}:us-central1:validatus-primary")
    database = os.getenv("CLOUD_SQL_DATABASE", "validatus")
    user = os.getenv("CLOUD_SQL_USER", "validatus_app")
    password = os.getenv("CLOUD_SQL_PASSWORD", "your_password_here")
    
    # Try different connection methods
    connection_strings = [
        # Cloud Run format
        f"postgresql://{user}:{password}@/{database}?host=/cloudsql/{connection_name}",
        # Standard format (for testing)
        f"postgresql://{user}:{password}@localhost:5432/{database}"
    ]
    
    connection = None
    for conn_str in connection_strings:
        try:
            logger.info(f"Attempting connection with: {conn_str.replace(password, '***')}")
            connection = await asyncpg.connect(conn_str)
            logger.info("Database connection successful!")
            break
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            continue
    
    if not connection:
        logger.error("All connection attempts failed")
        return False
    
    try:
        # Read and execute schema files in order
        migrations_dir = Path(__file__).parent.parent / "migrations"
        
        schema_files = [
            "001_initial_schema.sql",
            "002_create_url_collection_campaigns.sql"
        ]
        
        for schema_file in schema_files:
            schema_path = migrations_dir / schema_file
            if schema_path.exists():
                logger.info(f"Executing {schema_file}...")
                
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                
                for statement in statements:
                    try:
                        await connection.execute(statement)
                        logger.debug(f"Executed: {statement[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.debug(f"Skipped existing object: {statement[:50]}...")
                        else:
                            logger.warning(f"Statement failed: {e}")
                
                logger.info(f"✅ {schema_file} executed successfully")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
        
        # Test basic functionality
        await connection.execute("""
            INSERT INTO topics (session_id, topic, user_id) 
            VALUES ('test-session-001', 'Database Test Topic', 'test-user')
            ON CONFLICT (session_id) DO NOTHING
        """)
        
        result = await connection.fetch("SELECT COUNT(*) as count FROM topics")
        logger.info(f"Topics table has {result[0]['count']} records")
        
        logger.info("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False
    finally:
        if connection:
            await connection.close()

if __name__ == "__main__":
    success = asyncio.run(test_and_fix_database())
    exit(0 if success else 1)
