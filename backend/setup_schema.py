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
    
    # Database connection parameters
    password = os.getenv('CLOUD_SQL_PASSWORD', 'Validatus2024!')
    connection_string = f"postgresql://postgres:{password}@35.232.190.254:5432/validatusdb"
    
    print(f"Connecting to database...")
    print(f"Connection string: postgresql://postgres:***@35.232.190.254:5432/validatusdb")
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(connection_string)
        print("Connected to database successfully!")
        
        # Read the schema file
        schema_file = Path("migrations/001_initial_schema.sql")
        if not schema_file.exists():
            print(f"Schema file not found: {schema_file}")
            return False
            
        schema_content = schema_file.read_text()
        print(f"Schema file loaded: {schema_file}")
        
        # Execute the schema
        print("Executing database schema...")
        await conn.execute(schema_content)
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
        
        await conn.close()
        print("Database schema setup completed!")
        return True
        
    except Exception as e:
        print(f"Error setting up database schema: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database_schema())
    sys.exit(0 if success else 1)
