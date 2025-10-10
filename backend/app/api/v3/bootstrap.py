"""
Bootstrap API - Initialize v2.0 hierarchy and apply migrations
"""
from fastapi import APIRouter, HTTPException
import logging
import asyncio
from pathlib import Path

from ...core.database_config import db_manager

router = APIRouter()
logger = logging.getLogger(__name__)

# Advisory lock keys for bootstrap
HIERARCHY_LOCK_APP_ID = 42
HIERARCHY_LOCK_KEY = 1


@router.post("/run-migration")
async def run_migration():
    """Apply DEFERRABLE foreign key migration"""
    try:
        connection = await db_manager.get_connection()
        
        migration_path = Path(__file__).parent.parent.parent / "database" / "migrations" / "001_make_fks_deferrable.sql"
        
        if not migration_path.exists():
            raise HTTPException(status_code=500, detail=f"Migration file not found: {migration_path}")
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        logger.info("Applying DEFERRABLE FK migration...")
        await connection.execute(migration_sql)
        
        # Verify constraints
        verification_query = """
        SELECT 
            tc.table_name, 
            tc.constraint_name,
            con.condeferrable,
            con.condeferred
        FROM information_schema.table_constraints tc
        JOIN pg_constraint con ON con.conname = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name IN ('factors', 'layers', 'layer_scores', 'factor_calculations', 'segment_analysis')
        ORDER BY tc.table_name
        """
        
        results = await connection.fetch(verification_query)
        
        deferrable_fks = [
            {
                "table": row['table_name'],
                "constraint": row['constraint_name'],
                "deferrable": row['condeferrable'],
                "initially_deferred": row['condeferred']
            }
            for row in results
        ]
        
        return {
            "status": "success",
            "message": "Migration applied successfully",
            "deferrable_foreign_keys": deferrable_fks,
            "total_fks": len(deferrable_fks)
        }
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.post("/initialize-hierarchy")
async def initialize_hierarchy():
    """Bootstrap 5 segments and 28 factors with advisory lock protection"""
    try:
        # Import bootstrap function
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
        
        from bootstrap_hierarchy import bootstrap_hierarchy
        
        # Run bootstrap
        success = await bootstrap_hierarchy()
        
        if not success:
            raise HTTPException(status_code=500, detail="Bootstrap failed - check logs")
        
        # Get final counts
        connection = await db_manager.get_connection()
        seg_count = await connection.fetchval("SELECT COUNT(*) FROM segments")
        fac_count = await connection.fetchval("SELECT COUNT(*) FROM factors")
        lay_count = await connection.fetchval("SELECT COUNT(*) FROM layers")
        
        return {
            "status": "success",
            "message": "Hierarchy initialized successfully",
            "segments": seg_count,
            "factors": fac_count,
            "layers": lay_count,
            "advisory_lock_used": f"({HIERARCHY_LOCK_APP_ID}, {HIERARCHY_LOCK_KEY})"
        }
        
    except Exception as e:
        logger.error(f"Bootstrap failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bootstrap failed: {str(e)}")


@router.get("/hierarchy-status")
async def hierarchy_status():
    """Check current hierarchy status"""
    try:
        connection = await db_manager.get_connection()
        
        seg_count = await connection.fetchval("SELECT COUNT(*) FROM segments")
        fac_count = await connection.fetchval("SELECT COUNT(*) FROM factors")
        lay_count = await connection.fetchval("SELECT COUNT(*) FROM layers")
        score_count = await connection.fetchval("SELECT COUNT(*) FROM layer_scores")
        
        # Check FK constraints
        fk_query = """
        SELECT 
            tc.table_name,
            COUNT(*) as fk_count,
            SUM(CASE WHEN con.condeferrable THEN 1 ELSE 0 END) as deferrable_count
        FROM information_schema.table_constraints tc
        JOIN pg_constraint con ON con.conname = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name IN ('factors', 'layers', 'layer_scores', 'factor_calculations', 'segment_analysis')
        GROUP BY tc.table_name
        """
        
        fk_status = await connection.fetch(fk_query)
        
        return {
            "hierarchy": {
                "segments": seg_count,
                "factors": fac_count,
                "layers": lay_count,
                "layer_scores": score_count
            },
            "expected": {
                "segments": 5,
                "factors": 28,
                "layers": "210 (created on-demand)"
            },
            "status": {
                "segments_ok": seg_count == 5,
                "factors_ok": fac_count == 28,
                "ready_for_analysis": seg_count == 5 and fac_count == 28
            },
            "foreign_key_constraints": [
                {
                    "table": row['table_name'],
                    "total_fks": row['fk_count'],
                    "deferrable_fks": row['deferrable_count'],
                    "all_deferrable": row['fk_count'] == row['deferrable_count']
                }
                for row in fk_status
            ]
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

