import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, WebhookInfo
from loguru import logger

from app.features.story_creator.service import StoryCreatorService
from app.features.users.user_cache import UserCache
from app.ports.cache import Cache
from app.settings import get_settings
from app.telegram.handlers.start import start_router
from app.telegram.handlers.story_creation import story_creation_router
from app.telegram.middlewares import (
    setup_cache_middlewares,
    setup_i18n_middleware,
    setup_sessionmaker_middleware,
    setup_story_creator_middleware,
)

cfg = get_settings()


dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(story_creation_router)
bot = Bot(
    token=cfg.telegram.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML")
)
story_creator_service = StoryCreatorService()


async def start_listening_for_updates() -> asyncio.Task | None:
    match cfg.telegram.mode:
        case "polling":
            logger.info("Start polling for telegram bot updates")
            return asyncio.create_task(dp.start_polling(bot, skip_updates=True))
        case "webhook":
            logger.info("Set webhook for telegram bot updates")
            await set_webhook(bot)
            return None


async def set_webhook(my_bot: Bot) -> None:
    # Check and set webhook for Telegram
    async def check_webhook() -> WebhookInfo | None:
        try:
            webhook_info = await my_bot.get_webhook_info()
            return webhook_info
        except Exception as e:
            logger.error(f"Can't get webhook info - {e}")
            return

    current_webhook_info = await check_webhook()
    if current_webhook_info is None:
        return
    if cfg.debug:
        logger.debug(f"Current bot info: {current_webhook_info}")
    try:
        await my_bot.set_webhook(
            f"{cfg.telegram.base_webhook_url}{cfg.telegram.webhook_path}",
            secret_token=cfg.telegram.bot_token.get_secret_value(),
            drop_pending_updates=current_webhook_info.pending_update_count > 0,
            max_connections=40 if cfg.debug else 100,
        )
        if cfg.debug:
            logger.debug(f"Updated bot info: {await check_webhook()}")
    except Exception as e:
        logger.error(f"Can't set webhook - {e}")


async def set_bot_commands_menu(my_bot: Bot) -> None:
    # Register commands for Telegram bot (menu)
    commands = [
        BotCommand(command="/start", description="🚀 Start language learning"),
    ]
    try:
        await my_bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Can't set commands - {e}")


async def start_bot(cache: Cache, sessionmaker) -> None:
    """Initialize bot and setup middlewares"""
    # Set up FSM storage with Redis
    storage = RedisStorage.from_url(cfg.redis_url)
    dp.fsm.storage = storage

    setup_cache_middlewares(start_router, cache)
    setup_cache_middlewares(story_creation_router, cache)
    setup_sessionmaker_middleware(start_router, sessionmaker)
    setup_sessionmaker_middleware(story_creation_router, sessionmaker)
    await setup_story_creator_middleware(story_creation_router, story_creator_service, sessionmaker)

    # Setup i18n middleware
    # TODO: remove duplicated UserCache creation
    user_cache = UserCache(cache)
    await setup_i18n_middleware(start_router, user_cache, sessionmaker)
    await setup_i18n_middleware(story_creation_router, user_cache, sessionmaker)

    await set_bot_commands_menu(bot)
