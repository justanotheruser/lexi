from pydantic import SecretStr
from pydantic_settings import BaseSettings

from app.utils.custom_types import StringList


class OpenAIConfig(BaseSettings):
    model: str = "gpt-4o-mini"
    max_tokens: int = 400
    temperature: float = 0.8
    api_key: SecretStr = SecretStr("")


class StoryTellerConfig(BaseSettings):
    available_languages: StringList
    openai: OpenAIConfig
