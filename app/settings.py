"""
Configuration settings for Lexi bot
"""

from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class TelegramSettings(BaseSettings):
    bot_token: SecretStr = SecretStr("")
    mode: Literal["polling", "webhook"] = "polling"
    base_webhook_url: str = ""
    webhook_path: str = ""

    model_config = {
        "case_sensitive": False,
        "extra": "ignore",
    }


class LLMSettings(BaseSettings):
    openai_api_key: SecretStr = SecretStr("")

    model_config = {
        "case_sensitive": False,
        "extra": "ignore",
    }


class LanguageSettings(BaseSettings):
    """Language configuration settings"""

    # These will be populated from database at startup
    supported_languages: dict[str, str] = {}
    supported_languages_in_user_language: dict[str, dict[str, str]] = {}
    default_language_code: str = "en"

    model_config = {
        "case_sensitive": False,
        "extra": "ignore",
    }


class Settings(BaseSettings):
    """Application settings"""

    debug: bool = False

    telegram: TelegramSettings = TelegramSettings()
    llm: LLMSettings = LLMSettings()
    language: LanguageSettings = LanguageSettings()
    database_url: SecretStr = SecretStr("")

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # Logging
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }


@lru_cache
def get_settings():
    return Settings()
