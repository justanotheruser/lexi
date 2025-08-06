from pydantic import SecretStr
from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    host: str
    user: str
    password: SecretStr
    port: int
    db: int

    def build_url(self) -> str:
        return f"redis://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"
