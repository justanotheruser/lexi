import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, Message, WebhookInfo
from loguru import logger

from app.settings import get_settings

cfg = get_settings()

telegram_router = Router(name="telegram")
dp = Dispatcher()
dp.include_router(telegram_router)
bot = Bot(
    token=cfg.telegram.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML")
)


@telegram_router.message(F.text == "/id")
async def handle_id_command(message: Message) -> None:
    """Handle /id command and return user ID"""
    if message.from_user is None:
        await message.reply("❌ Unable to get user information")
        return

    user_id = message.from_user.id
    user_name = message.from_user.full_name or message.from_user.username or "Unknown"

    response = f"🆔 <b>Your Information:</b>\n\n"
    response += f"👤 <b>Name:</b> {user_name}\n"
    response += f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
    response += f"📝 <b>Username:</b> @{message.from_user.username or 'None'}\n"

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
        BotCommand(command="/id", description="👋 Get my ID"),
    ]
    try:
        await my_bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Can't set commands - {e}")


async def start_bot():
    await set_bot_commands_menu(bot)
