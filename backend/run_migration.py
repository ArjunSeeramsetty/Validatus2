#!/usr/bin/env python3
"""
Database Migration Script for Google Custom Search Integration
Run this script to create the missing tables for URL collection campaigns.
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.gcp_persistence_config import get_gcp_persistence_settings

async def run_migration():
    """Run the database migration to create missing tables"""
    
    print("🗄️ Starting database migration for Google Custom Search integration...")
    
    try:
        # Get database configuration
        settings = get_gcp_persistence_settings()
        
        # Build connection string
        if settings.local_development_mode:
            # Local development - use SQLite
            print("⚠️ Running in local development mode - skipping Cloud SQL migration")
            return
        
        # Cloud SQL connection
        password = settings.get_secret("cloud-sql-password")
        connection_string = f"postgresql://{settings.cloud_sql_user}:{password}@{settings.cloud_sql_connection_name.split(':')[2]}/{settings.cloud_sql_database}"
        
        print(f"🔌 Connecting to Cloud SQL database...")
        print(f"Database: {settings.cloud_sql_database}")
        print(f"Instance: {settings.cloud_sql_connection_name}")
        
        # Connect to database
        conn = await asyncpg.connect(connection_string)
        
        print("✅ Connected to database successfully!")
        
        # Read and execute migration SQL
        migration_file = Path(__file__).parent / "migrations" / "002_create_url_collection_campaigns.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return
        
        print(f"📄 Reading migration file: {migration_file}")
        migration_sql = migration_file.read_text()
        
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
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_migration())
