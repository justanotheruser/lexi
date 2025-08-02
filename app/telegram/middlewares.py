from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.features.users.user_cache import UserCache
from app.ports.cache import Cache
from app.telegram.middleware.depends import depends


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
