#!/usr/bin/env python3
"""
Script to create the missing workflow_status table
"""
import asyncio
import asyncpg
import os
import sys

async def create_workflow_status_table():
    """Create the workflow_status table if it doesn't exist"""
    
    # Require all connection parameters from environment
    password = os.getenv('CLOUD_SQL_PASSWORD')
    if not password:
        raise ValueError("CLOUD_SQL_PASSWORD environment variable must be set")
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'validatusdb')
    db_user = os.getenv('DB_USER', 'validatus_app')
    
    connection_string = f"postgresql://{db_user}:{password}@{db_host}:{db_port}/{db_name}"
    
    print(f"Connecting to database...")
    
    try:
        # Connect to the database with timeout and proper cleanup
        async with asyncpg.connect(connection_string, timeout=10) as conn:
            print("Connected to database successfully!")
            
            # Check if workflow_status table exists
            check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'workflow_status'
            )
            """
            exists = await conn.fetchval(check_query)
            
            if exists:
                print("workflow_status table already exists!")
            else:
                print("Creating workflow_status table...")
                
                # Create workflow_status table
                create_table_query = """
                CREATE TABLE workflow_status (
                    session_id VARCHAR(50) PRIMARY KEY REFERENCES topics(session_id) ON DELETE CASCADE,
                    current_stage VARCHAR(50) NOT NULL,
                    stages_completed TEXT[] DEFAULT '{}',
                    stage_progress JSONB DEFAULT '{}'::jsonb,
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    
                    -- Add constraints
                    CONSTRAINT chk_current_stage CHECK (current_stage IN (
                        'CREATED', 'URL_COLLECTION', 'URL_SCRAPING', 'CONTENT_PROCESSING', 
                        'VECTOR_CREATION', 'ANALYSIS', 'COMPLETED', 'FAILED'
                    ))
                );
                """
                
                await conn.execute(create_table_query)
                print("workflow_status table created successfully!")
                
                # Create indexes
                index_queries = [
                    "CREATE INDEX idx_workflow_status_stage ON workflow_status(current_stage);",
                    "CREATE INDEX idx_workflow_status_updated ON workflow_status(updated_at DESC);"
                ]
                
                for query in index_queries:
                    await conn.execute(query)
                print("Indexes created successfully!")
                
                # Create trigger for updated_at
                trigger_query = """
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
                
                CREATE TRIGGER update_workflow_status_updated_at BEFORE UPDATE ON workflow_status
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                """
                
                await conn.execute(trigger_query)
                print("Trigger created successfully!")
            
            print("Database setup completed!")
            return True
        
    except Exception as e:
        print(f"Error creating workflow_status table: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_workflow_status_table())
    sys.exit(0 if success else 1)
