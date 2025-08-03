from pydantic_settings import BaseSettings


class ServerConfig(BaseSettings):
    port: int
    host: str
    url: str

    def build_url(self, path: str) -> str:
        return f"{self.url}{path}"
