from pydantic import SecretStr
from pydantic_settings import BaseSettings

from lexi.utils.custom_types import StringList


class OpenAIConfig(BaseSettings):
    model: str = "gpt-4o-mini"
    max_tokens: int = 600
    temperature: float = 0.9
    api_key: SecretStr = SecretStr("")


class StoryTellerConfig(BaseSettings):
    available_languages: StringList
    openai: OpenAIConfig
