"""
Configuration settings for Lexi bot
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Lexi"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI
    openai_api_key: str
    
    # Telegram
    telegram_bot_token: str
    
    # Database
    database_url: str = "postgresql://lexi:lexi123@db:5432/lexi_dev"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 