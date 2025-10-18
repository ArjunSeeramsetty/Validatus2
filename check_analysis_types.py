#!/usr/bin/env python3
"""
Check what analysis types exist for a session
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database_config import db_manager

async def check_analysis_types(session_id):
    """Check what analysis types exist for a session"""
    try:
        conn = await db_manager.get_connection()
        
        # Check what analysis types exist
        result = await conn.fetch(
            "SELECT DISTINCT analysis_type FROM analysis_results WHERE session_id = $1",
            session_id
        )
        
        print(f"Analysis types found for session {session_id}:")
        if result:
            for row in result:
                print(f"  - {row['analysis_type']}")
        else:
            print("  No analysis results found")
            
        # Also check if there are any results at all
        count_result = await conn.fetchrow(
            "SELECT COUNT(*) as count FROM analysis_results WHERE session_id = $1",
            session_id
        )
        
        print(f"Total analysis results: {count_result['count'] if count_result else 0}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    session_id = "topic-747b5405721c"
    asyncio.run(check_analysis_types(session_id))
