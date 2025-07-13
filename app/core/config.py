from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_CLOUD_CREDENTIALS_PATH: Optional[str] = os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH")
    AZURE_SPEECH_KEY: Optional[str] = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION: Optional[str] = os.getenv("AZURE_SPEECH_REGION")
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./commercial_real_estate.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Audio Settings
    AUDIO_SAMPLE_RATE: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    AUDIO_CHUNK_SIZE: int = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
    MAX_AUDIO_DURATION: int = int(os.getenv("MAX_AUDIO_DURATION", "300"))
    
    # LLM Settings
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P: float = float(os.getenv("TOP_P", "1.0"))
    
    # RAG Settings
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "faiss")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_DOCUMENTS: int = int(os.getenv("TOP_K_DOCUMENTS", "5"))
    
    # TTS Settings
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "openai")
    VOICE_ID: str = os.getenv("VOICE_ID", "alloy")
    SPEECH_RATE: float = float(os.getenv("SPEECH_RATE", "1.0"))

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()