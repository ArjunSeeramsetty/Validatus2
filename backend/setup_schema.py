#!/usr/bin/env python3
"""
Script to set up the database schema for Cloud SQL
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

async def setup_database_schema():
    """Set up the database schema"""
    
    # Require all connection parameters from environment
    password = os.getenv('CLOUD_SQL_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER', 'postgres')
    
    if not all([password, db_host, db_name]):
        print("Error: Missing required environment variables (CLOUD_SQL_PASSWORD, DB_HOST, DB_NAME)")
        return False
    
    connection_string = f"postgresql://{db_user}:{password}@{db_host}:{db_port}/{db_name}"
    
    print(f"Connecting to database...")
    print(f"Connection string: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    
    try:
        # Connect to the database with timeout and proper cleanup
        async with asyncpg.connect(connection_string, timeout=10) as conn:
            print("Connected to database successfully!")
            
            # Read the schema file
            schema_file = Path("migrations/001_initial_schema.sql")
            if not schema_file.exists():
                print(f"Schema file not found: {schema_file}")
                return False
                
            schema_content = schema_file.read_text()
            print(f"Schema file loaded: {schema_file}")
            
            # Execute the schema - split and execute statements individually
            print("Executing database schema...")
            # Split and execute statements individually to support multiple DDL commands
            for statement in schema_content.split(';'):
                statement = statement.strip()
                if statement:  # Skip empty statements
                    await conn.execute(statement)
            print("Database schema executed successfully!")
            
            # Verify tables were created
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
            """
            tables = await conn.fetch(tables_query)
            
            print("Created tables:")
            for table in tables:
                print(f"  - {table['table_name']}")
            
            print("Database schema setup completed!")
            return True
        
    except Exception as e:
        print(f"Error setting up database schema: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database_schema())
    sys.exit(0 if success else 1)
