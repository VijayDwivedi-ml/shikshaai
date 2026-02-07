import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Async-safe configuration with validation"""
    
    # Required
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Optional with defaults
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "teaching-agent")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Async/performance settings
    MAX_CONCURRENT_TASKS: int = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Firebase (optional for future)
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID")
    USE_CACHE: bool = os.getenv("USE_CACHE", "False").lower() == "true"
    
    class Config:
        env_file = ".env"
    
    def validate(self):
        """Async validation that can be called at startup"""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Get one from: https://makersuite.google.com/app/apikey")
        if len(self.GEMINI_API_KEY) < 20:
            raise ValueError("Invalid GEMINI_API_KEY format")
        
        # Validate async settings
        if self.MAX_CONCURRENT_TASKS < 1 or self.MAX_CONCURRENT_TASKS > 20:
            raise ValueError("MAX_CONCURRENT_TASKS must be between 1 and 20")
            
        return True

# Global settings instance
settings = Settings()