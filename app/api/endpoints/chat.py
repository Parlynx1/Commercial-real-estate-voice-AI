from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

llm_service = LLMService()

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []
    rag_context: Optional[str] = None
    emotion_data: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    processing_time: float
    tokens_used: int
    model: str
    rag_sources_used: bool

@router.post("/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """
    Process chat message with LLM, property matching, and emotion awareness
    """
    try:
        # Generate response
        result = await llm_service.generate_response(
            conversation_history=request.conversation_history,
            new_message=request.message,
            rag_context=request.rag_context,
            emotion_data=request.emotion_data
        )
        
        return ChatResponse(
            response=result["response"],
            processing_time=result["processing_time"],
            tokens_used=result["tokens_used"],
            model=result["model"],
            rag_sources_used=bool(request.rag_context)
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))