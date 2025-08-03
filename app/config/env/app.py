from pydantic_settings import BaseSettings, SettingsConfigDict

from app.const import ENV_FILE

from .common import CommonConfig
from .content_moderation import ContentModerationConfig
from .postgres import PostgresConfig
from .redis import RedisConfig
from .server import ServerConfig
from .sql_alchemy import SQLAlchemyConfig
from .story_teller import StoryTellerConfig
from .telegram import TelegramConfig


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )
    telegram: TelegramConfig
    postgres: PostgresConfig
    sql_alchemy: SQLAlchemyConfig = SQLAlchemyConfig()
    redis: RedisConfig
    server: ServerConfig
    common: CommonConfig
    story_teller: StoryTellerConfig
    content_moderation: ContentModerationConfig = ContentModerationConfig()
