#!/usr/bin/env python3
"""Simple database connection test"""
import asyncio
import asyncpg
import os

async def test_simple_connection():
    # Test with environment variable
    password = os.getenv('CLOUD_SQL_PASSWORD', 'Validatus2024!')
    print(f"Using password: {password}")
    
    # Test connection string
    connection_string = f"postgresql://postgres:{password}@/validatusdb?host=/cloudsql/validatus-platform:us-central1-c:validatus-sql"
    print(f"Connection string: postgresql://postgres:***@/validatusdb?host=/cloudsql/validatus-platform:us-central1-c:validatus-sql")
    
    try:
        conn = await asyncpg.connect(connection_string)
        print("✅ Connection successful!")
        
        # Test a simple query
        result = await conn.fetchval("SELECT version()")
        print(f"PostgreSQL version: {result}")
        
        # Check if topics table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'topics'
            )
        """)
        print(f"Topics table exists: {table_exists}")
        
        if table_exists:
            # Check table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'topics' 
                ORDER BY ordinal_position
            """)
            print("Topics table columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_connection())
