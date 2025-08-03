from pydantic import SecretStr
from pydantic_settings import BaseSettings


class TelegramConfig(BaseSettings):
    bot_token: SecretStr
    # locales: list[str]
    drop_pending_updates: bool
    use_webhook: bool
    reset_webhook: bool
    webhook_path: str
    webhook_secret: SecretStr
