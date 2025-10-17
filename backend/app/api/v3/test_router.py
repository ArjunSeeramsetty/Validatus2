# backend/app/api/v3/test_router.py

"""
Minimal test router to verify registration works
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    """Simple test endpoint"""
    return {"message": "Hello from test router", "status": "working"}
