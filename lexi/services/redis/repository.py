from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final, Optional, TypeVar, cast

from pydantic import BaseModel, TypeAdapter
from redis.asyncio import Redis
from redis.typing import ExpiryT

from lexi.utils import mjson
from lexi.utils.key_builder import StorageKey

if TYPE_CHECKING:
    from lexi.config import AppConfig

T = TypeVar("T", bound=Any)

logger: Final[logging.Logger] = logging.getLogger(name=__name__)
TX_QUEUE_KEY: Final[str] = "tx_queue"


class RedisRepository:
    client: Redis
    config: AppConfig

    def __init__(self, client: Redis, config: AppConfig) -> None:
        self.client = client
        self.config = config

    async def get(
        self,
        key: StorageKey,
        validator: type[T],
        default: Optional[T] = None,
    ) -> Optional[T]:
        value: Optional[Any] = await self.client.get(key.pack())
        if value is None:
            return default
        value = mjson.decode(value)
        return TypeAdapter[T](validator).validate_python(value)

    async def set(self, key: StorageKey, value: Any, ex: Optional[ExpiryT] = None) -> None:
        if isinstance(value, BaseModel):
            value = value.model_dump(exclude_defaults=True)
        await self.client.set(name=key.pack(), value=mjson.encode(value), ex=ex)

    async def exists(self, key: StorageKey) -> bool:
        return cast(bool, await self.client.exists(key.pack()))

    async def delete(self, key: StorageKey) -> None:
        await self.client.delete(key.pack())

    async def close(self) -> None:
        await self.client.aclose(close_connection_pool=True)  # type: ignore
