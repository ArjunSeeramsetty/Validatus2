#!/usr/bin/env python3
"""
Script to verify and set up the complete database schema with all tables and relationships
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

async def verify_and_setup_schema():
    """Verify and set up the complete database schema"""
    
    # Database connection parameters
    password = os.getenv('CLOUD_SQL_PASSWORD', 'Validatus2024!')
    connection_string = f"postgresql://postgres:{password}@35.232.190.254:5432/validatusdb"
    
    print("Connecting to database...")
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(connection_string)
        print("Connected to database successfully!")
        
        # Read the complete schema file
        schema_file = Path("migrations/001_initial_schema.sql")
        if not schema_file.exists():
            print(f"Schema file not found: {schema_file}")
            return False
            
        schema_content = schema_file.read_text()
        print(f"Schema file loaded: {schema_file}")
        
        # Split schema into individual statements
        statements = []
        current_statement = []
        
        for line in schema_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_statement.append(line)
                if line.endswith(';'):
                    statements.append('\n'.join(current_statement))
                    current_statement = []
        
        print(f"Found {len(statements)} SQL statements to execute")
        
        # Execute each statement individually with error handling
        executed_count = 0
        skipped_count = 0
        error_count = 0
        
        for i, statement in enumerate(stateries, 1):
            try:
                await conn.execute(statement)
                executed_count += 1
                print(f"[{i}/{len(statements)}] Executed successfully")
            except Exception as e:
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ['already exists', 'duplicate', 'already present']):
                    skipped_count += 1
                    print(f"[{i}/{len(statements)}] Skipped (already exists): {statement[:50]}...")
                else:
                    error_count += 1
                    print(f"[{i}/{len(statements)}] Error: {e}")
                    print(f"Statement: {statement[:100]}...")
        
        print(f"\nExecution Summary:")
        print(f"  Executed: {executed_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Errors: {error_count}")
        
        # Verify all tables exist
        print("\nVerifying tables...")
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        """
        tables = await conn.fetch(tables_query)
        
        expected_tables = [
            'topics', 'topic_urls', 'workflow_status', 'vector_embeddings', 
            'analysis_sessions', 'workflow_checkpoints'
        ]
        
        existing_tables = [table['table_name'] for table in tables]
        
        print("Existing tables:")
        for table in existing_tables:
            status = "✓" if table in expected_tables else "?"
            print(f"  {status} {table}")
        
        missing_tables = set(expected_tables) - set(existing_tables)
        if missing_tables:
            print(f"\nMissing tables: {missing_tables}")
            return False
        
        # Verify foreign key relationships
        print("\nVerifying foreign key relationships...")
        fk_query = """
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_schema = 'public'
        ORDER BY tc.table_name, kcu.column_name
        """
        
        foreign_keys = await conn.fetch(fk_query)
        print("Foreign key relationships:")
        for fk in foreign_keys:
            print(f"  {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        # Verify indexes
        print("\nVerifying indexes...")
        index_query = """
        SELECT indexname, tablename 
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname
        """
        indexes = await conn.fetch(index_query)
        print("Indexes:")
        for index in indexes:
            print(f"  {index['tablename']}.{index['indexname']}")
        
        await conn.close()
        print("\nDatabase schema verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error setting up database schema: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_and_setup_schema())
    sys.exit(0 if success else 1)
