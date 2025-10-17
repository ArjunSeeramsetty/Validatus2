"""
Simple Test API
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v3/test", tags=["test"])

@router.get("/simple")
async def test_simple():
    return {"message": "Simple test endpoint working", "status": "success"}
