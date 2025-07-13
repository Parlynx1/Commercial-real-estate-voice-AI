from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Commercial Real Estate Voice AI",
    description="Bidirectional Voice Conversational AI for Commercial Real Estate",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/")
async def root():
    return {
        "message": "Commercial Real Estate Voice AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "development"}

# Simple test endpoints to start with
@app.post("/api/v1/test-transcribe")
async def test_transcribe():
    return {
        "transcript": "This is a test transcription",
        "confidence": 0.95,
        "transcription_time": 1.2,
        "provider": "test",
        "emotion_analysis": {
            "emotion_score": 0.7,
            "enthusiasm_level": 0.8,
            "voice_pace": 1.0,
            "tone_analysis": {"professional": 0.7, "excited": 0.6}
        }
    }

@app.post("/api/v1/test-chat")
async def test_chat():
    return {
        "response": "I'd be happy to help you find the perfect commercial space! Tell me about your business needs.",
        "processing_time": 1.5,
        "tokens_used": 50,
        "model": "test-model",
        "rag_sources_used": False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )