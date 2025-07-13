from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from app.services.transcription_service import TranscriptionService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

transcription_service = TranscriptionService()

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    provider: str = Form("openai")
):
    """
    Transcribe audio to text with emotion analysis
    """
    try:
        # Validate audio file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Transcribe with emotion analysis
        result = await transcription_service.transcribe_audio(audio_data, provider)
        
        return {
            "transcript": result["transcript"],
            "confidence": result.get("confidence"),
            "transcription_time": result["transcription_time"],
            "provider": result["provider"],
            "emotion_analysis": {
                "emotion_score": result.get("emotion_score", 0.5),
                "enthusiasm_level": result.get("enthusiasm_level", 0.5),
                "voice_pace": result.get("voice_pace", 1.0),
                "tone_analysis": result.get("tone_analysis", {})
            }
        }
        
    except Exception as e:
        logger.error(f"Transcription endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
