from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.features.story_creator.service import StoryCreatorService
from app.features.users.user_cache import UserCache
from app.ports.cache import Cache
from app.telegram.i18n import I18nService
from app.telegram.middleware.depends import depends
from app.telegram.middleware.i18n_middleware import I18nMiddleware


def setup_cache_middlewares(router: Router, cache: Cache) -> None:
    """Set up cache middlewares for all handlers"""
    user_cache = UserCache(cache)
    user_cache_middleware = depends("user_cache", user_cache)
    router.message.middleware(user_cache_middleware)
    router.callback_query.middleware(user_cache_middleware)


def setup_sessionmaker_middleware(
    router: Router, sessionmaker: async_sessionmaker[AsyncSession]
) -> None:
    """Set up database session middleware for all handlers"""
    sessionmaker_middleware = depends("sessionmaker", sessionmaker)
    router.message.middleware(sessionmaker_middleware)
    router.callback_query.middleware(sessionmaker_middleware)


def setup_i18n_middleware(router: Router, user_cache: UserCache) -> None:
    """Set up i18n middleware for all handlers"""
    i18n_service = I18nService(user_cache)
    i18n_middleware = I18nMiddleware(i18n_service)
    router.message.middleware(i18n_middleware)
    router.callback_query.middleware(i18n_middleware)


async def setup_story_creator_middleware(
    router: Router, story_creator_service: StoryCreatorService, sessionmaker
) -> None:
    """Set up story creator middleware for all handlers"""
    await story_creator_service.start(sessionmaker)
    story_creator_middleware = depends("story_creator", story_creator_service)
    router.message.middleware(story_creator_middleware)
    router.callback_query.middleware(story_creator_middleware)
