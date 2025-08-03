from pydantic import SecretStr
from pydantic_settings import BaseSettings

from app.utils.custom_types import StringList


class StoryTellerConfig(BaseSettings):
    available_languages: StringList
    openai_api_key: SecretStr
