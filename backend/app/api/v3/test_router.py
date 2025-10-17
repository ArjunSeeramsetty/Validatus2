# backend/app/api/v3/test_router.py

"""
Minimal test router to verify registration works
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v3/test", tags=["test"])

@router.get("/hello")
async def hello():
    """Simple test endpoint"""
    return {"message": "Hello from test router", "status": "working"}
