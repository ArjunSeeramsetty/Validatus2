#!/usr/bin/env python3
"""Test Cloud SQL connection directly"""
import asyncio
import asyncpg
import os
from google.cloud import secretmanager

async def test_connection():
    # Get password from Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/validatus-platform/secrets/cloud-sql-password/versions/latest"
    response = client.access_secret_version(request={"name": name})
    password = response.payload.data.decode("UTF-8")
    
    print(f"Retrieved password: {password}")
    
    # Test connection string
    connection_string = f"postgresql://validatus_app:{password}@/validatusdb?host=/cloudsql/validatus-platform:us-central1-c:validatus-sql"
    print(f"Connection string: {connection_string}")
    
    try:
        conn = await asyncpg.connect(connection_string)
        print("✅ Connection successful!")
        
        # Test a simple query
        result = await conn.fetchval("SELECT version()")
        print(f"PostgreSQL version: {result}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
