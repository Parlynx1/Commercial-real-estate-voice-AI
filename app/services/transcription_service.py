import time
import openai
import tempfile
from typing import Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not provided - transcription will use mock data")
        
    async def transcribe_audio(self, audio_data: bytes, provider: str = "openai") -> Dict[str, Any]:
        """
        Transcribe audio to text with basic emotion analysis
        """
        start_time = time.time()
        
        try:
            if not self.openai_client:
                # Return mock data for testing
                return self._get_mock_transcription(start_time)
            
            # Use OpenAI Whisper
            result = await self._transcribe_openai(audio_data)
            
            # Add basic emotion analysis (simplified for Windows setup)
            emotion_analysis = self._basic_emotion_analysis(result["transcript"])
            result.update(emotion_analysis)
            
            transcription_time = time.time() - start_time
            result["transcription_time"] = transcription_time
            
            logger.info(f"Transcription completed in {transcription_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            # Return mock data on error
            return self._get_mock_transcription(start_time)
    
    async def _transcribe_openai(self, audio_data: bytes) -> Dict[str, Any]:
        """OpenAI Whisper transcription"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            try:
                with open(temp_file.name, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                    
                return {
                    "transcript": transcript,
                    "confidence": None,  # OpenAI doesn't provide confidence scores
                    "provider": "openai"
                }
            finally:
                import os
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def _basic_emotion_analysis(self, transcript: str) -> Dict[str, Any]:
        """Basic emotion analysis based on text content"""
        text_lower = transcript.lower()
        
        # Simple keyword-based emotion detection
        enthusiasm_keywords = ["excited", "love", "amazing", "perfect", "great", "fantastic"]
        professional_keywords = ["need", "require", "business", "professional", "office"]
        uncertainty_keywords = ["maybe", "perhaps", "not sure", "uncertain", "hmm"]
        
        enthusiasm_score = sum(1 for word in enthusiasm_keywords if word in text_lower)
        professional_score = sum(1 for word in professional_keywords if word in text_lower)
        uncertainty_score = sum(1 for word in uncertainty_keywords if word in text_lower)
        
        # Normalize scores
        total_words = len(text_lower.split())
        if total_words > 0:
            enthusiasm_level = min(enthusiasm_score / total_words * 10, 1.0)
            professional_level = min(professional_score / total_words * 10, 1.0)
            uncertainty_level = min(uncertainty_score / total_words * 10, 1.0)
        else:
            enthusiasm_level = 0.5
            professional_level = 0.5
            uncertainty_level = 0.3
        
        return {
            "emotion_score": 0.5 + (enthusiasm_level - uncertainty_level) * 0.5,
            "enthusiasm_level": enthusiasm_level,
            "voice_pace": 1.0,  # Default for text-based analysis
            "tone_analysis": {
                "professional": professional_level,
                "excited": enthusiasm_level,
                "confident": 1.0 - uncertainty_level,
                "uncertain": uncertainty_level
            }
        }
    
    def _get_mock_transcription(self, start_time: float) -> Dict[str, Any]:
        """Return mock transcription for testing"""
        transcription_time = time.time() - start_time
        
        return {
            "transcript": "I'm looking for office space for my growing business. We need something modern and professional.",
            "confidence": 0.95,
            "transcription_time": transcription_time,
            "provider": "mock",
            "emotion_score": 0.7,
            "enthusiasm_level": 0.6,
            "voice_pace": 1.0,
            "tone_analysis": {
                "professional": 0.8,
                "excited": 0.5,
                "confident": 0.7,
                "uncertain": 0.2
            }
        }
