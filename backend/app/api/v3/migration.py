"""
Database Migration API Endpoints
"""

from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from run_migration import run_migration
import asyncio

router = APIRouter(prefix="/migration", tags=["migration"])

@router.post("/run")
async def run_database_migration():
    """
    Run database migration to create missing tables for Google Custom Search integration
    """
    try:
        await run_migration()
        return {
            "status": "success",
            "message": "Database migration completed successfully",
            "details": "Created url_collection_campaigns and search_queries tables"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {str(e)}"
        )
