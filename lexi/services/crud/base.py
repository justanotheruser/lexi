from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lexi.config import AppConfig
from lexi.services.base import BaseService


class CrudService(BaseService):
    session_pool: async_sessionmaker[AsyncSession]
    redis: Redis
    config: AppConfig

    def __init__(
        self,
        session_pool: async_sessionmaker[AsyncSession],
        redis: Redis,
        config: AppConfig,
    ) -> None:
        super().__init__()
        self.session_pool = session_pool
        self.redis = redis
        self.config = config
