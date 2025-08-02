"""
Configuration settings for Lexi bot
"""

from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Language

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

    # Database
    database_url: str = "postgresql://lexi:lexi123@db:5432/lexi_dev"

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


async def load_language_data(session: AsyncSession):
    """Load language data from database and return as dictionaries"""
    # Get all language records
    result = await session.execute(select(Language))
    language_records = result.scalars().all()

    supported_languages = {}
    supported_languages_in_user_language = {}

    for record in language_records:
        # For supported_languages, we want where language_code == user_language_code
        if record.language_code == record.user_language_code:
            supported_languages[record.language_code] = record.word

        # For supported_languages_in_user_language, group by user_language_code
        if record.user_language_code not in supported_languages_in_user_language:
            supported_languages_in_user_language[record.user_language_code] = {}
        supported_languages_in_user_language[record.user_language_code][
            record.language_code
        ] = record.word

    return supported_languages, supported_languages_in_user_language
