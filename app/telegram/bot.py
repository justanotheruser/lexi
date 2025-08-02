import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, Message, User, WebhookInfo
from loguru import logger

from app.settings import get_settings
from app.utils.language import (
    find_best_language_match,
    get_language_confirmation_message,
    get_language_name_in_user_language,
    get_language_not_supported_message,
    get_learning_phrase_in_target_language,
    get_user_language_message,
)

cfg = get_settings()

telegram_router = Router(name="telegram")
dp = Dispatcher()
dp.include_router(telegram_router)
bot = Bot(
    token=cfg.telegram.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML")
)


@telegram_router.message(F.text == "/start")
async def handle_start_command(message: Message) -> None:
    """""Get user settings and ask user for story language selection""" ""
    tg_user: User = message.from_user  # type: ignore[assignment]
    if (user := await user_cache.get(tg_user.id)) is None:
        user = await get_or_create_user(ui_language_code=tg_user.language_code)
        await user_cache.set(user.id, user)
        # session = await get_session()
        # if (user := await select(User, id=tg_user.id)) is None:

    # Get user's language (default to English if not available)
    # user_language = message.from_user.language_code or "en"

    # Get the language selection message in user's language
    # language_message = get_user_language_message(user_language)

    # await message.reply(language_message)


@telegram_router.message(F.text)
async def handle_language_selection(message: Message) -> None:
    """Handle language selection from user input"""
    if message.from_user is None or message.text is None:
        return

    user_input = message.text.strip()

    # Get user's language for localized messages
    user_language = message.from_user.language_code or "en"

    # Find the best matching language
    language_code, confidence = find_best_language_match(
        user_input,
        cfg.language.supported_languages,
        user_language,
        cfg.language.supported_languages_in_user_language,
    )

    if language_code:
        # Language found - send confirmation
        # Get language name in user's native language
        language_name_in_user_lang = get_language_name_in_user_language(
            language_code, user_language, cfg.language.supported_languages_in_user_language
        )

        # Get confirmation message in user's language
        confirmation_message = get_language_confirmation_message(user_language)

        # Get learning phrase in target language
        learning_phrase = get_learning_phrase_in_target_language(language_code)

        # Combine messages
        response = (
            f"✅ {confirmation_message} <b>{language_name_in_user_lang}</b>!\n\n{learning_phrase}"
        )
        await message.reply(response)
    else:
        # Language not supported
        error_message = get_language_not_supported_message(user_language)
        response = f"❌ {error_message}"
        await message.reply(response)


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


async def start_bot():
    await set_bot_commands_menu(bot)
