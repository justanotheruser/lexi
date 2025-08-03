from pydantic import SecretStr
from pydantic_settings import BaseSettings


class ContentModerationConfig(BaseSettings):
    openai_api_key: SecretStr = SecretStr("")
    is_enabled: bool = True
