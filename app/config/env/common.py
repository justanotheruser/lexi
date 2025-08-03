from pydantic_settings import BaseSettings


class CommonConfig(BaseSettings):
    admin_chat_id: int
