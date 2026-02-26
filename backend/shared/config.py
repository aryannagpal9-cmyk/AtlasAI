import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_role_key: str
    
    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    
    # App
    debug: bool = False
    cors_origins: str 
    
    # Internal
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Global settings instance
settings = Settings()
