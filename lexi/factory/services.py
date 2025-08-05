from __future__ import annotations

from typing import Any, TypedDict

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lexi.config import AppConfig
from lexi.services.crud import UserService
from lexi.services.redis import RedisRepository
from lexi.services.story_creator import StoryCreatorService
from lexi.services.story_teller import StoryTellerService


class Services(TypedDict):
    redis_repository: RedisRepository
    user_service: UserService
    story_creator: StoryCreatorService
    story_teller: StoryTellerService


def create_services(
    session_pool: async_sessionmaker[AsyncSession],
    redis: Redis,
    config: AppConfig,
) -> Services:
    crud_service_kwargs: dict[str, Any] = {
        "session_pool": session_pool,
        "redis": redis,
        "config": config,
    }

    redis_repository: RedisRepository = RedisRepository(client=redis, config=config)
    user_service: UserService = UserService(**crud_service_kwargs)
    story_creator: StoryCreatorService = StoryCreatorService(
        config=config, user_service=user_service
    )
    story_teller: StoryTellerService = StoryTellerService(
        config=config, redis_repo=redis_repository
    )

    return Services(
        redis_repository=redis_repository,
        user_service=user_service,
        story_creator=story_creator,
        story_teller=story_teller,
    )
