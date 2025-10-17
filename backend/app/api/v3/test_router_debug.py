# test_router_debug.py

"""
Debug router registration by creating a minimal test router
"""

from fastapi import APIRouter

# Create a minimal router with no dependencies
test_router = APIRouter(prefix="/api/v3/test-debug", tags=["debug"])

@test_router.get("/ping")
async def ping():
    """Simple ping endpoint to test router registration"""
    return {"message": "Router registration test successful", "status": "ok"}
