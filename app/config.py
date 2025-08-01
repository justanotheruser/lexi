"""
Configuration settings for Lexi bot
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    debug: bool = False
    openai_api_key: SecretStr = SecretStr("")
    telegram_bot_token: SecretStr = SecretStr("")

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
        """Pydantic configuration settings."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
