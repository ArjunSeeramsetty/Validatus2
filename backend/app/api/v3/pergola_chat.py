"""
Pergola Chat API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.pergola_chat_service import PergolaChatService

router = APIRouter(prefix="/api/v3/chat", tags=["pergola_chat"])

class ChatRequest(BaseModel):
    message: str
    segment: str = "general"  # general, consumer, market, product, brand, business_case, experience
    conversation_history: Optional[List[Dict]] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    segment: str
    timestamp: str

# Initialize chat service
chat_service = PergolaChatService()

@router.post("/pergola", response_model=ChatResponse)
async def chat_with_pergola_analysis(request: ChatRequest):
    """Chat with pergola analysis data"""
    try:
        result = await chat_service.chat(
            message=request.message,
            segment=request.segment,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/segments")
async def get_available_segments():
    """Get available chat segments"""
    return {
        "segments": [
            {"id": "general", "name": "General Analysis", "description": "Overall pergola market insights"},
            {"id": "consumer", "name": "Consumer Intelligence", "description": "Consumer behavior and demographics"},
            {"id": "market", "name": "Market Analysis", "description": "Market trends and opportunities"}, 
            {"id": "product", "name": "Product Intelligence", "description": "Product differentiation and innovation"},
            {"id": "brand", "name": "Brand Intelligence", "description": "Brand positioning and perception"},
            {"id": "business_case", "name": "Business Case", "description": "Financial analysis and ROI"},
            {"id": "experience", "name": "Customer Experience", "description": "Customer journey and service excellence"}
        ]
    }

@router.get("/health")
async def chat_health_check():
    """Health check for chat service"""
    return {"status": "healthy", "service": "pergola_chat"}
