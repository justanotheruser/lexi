from pydantic import SecretStr
from pydantic_settings import BaseSettings

from app.utils.custom_types import StringList


class TelegramConfig(BaseSettings):
    bot_token: SecretStr
    locales: StringList
    drop_pending_updates: bool
    use_webhook: bool
    reset_webhook: bool
    webhook_path: str
    webhook_secret: SecretStr
