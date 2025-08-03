from typing import Annotated

from aiogram import types
from fastapi import APIRouter, Header
from loguru import logger

from app.bot import bot, dp
from app.settings import get_settings

cfg = get_settings()

root_router = APIRouter(
    prefix="",
    tags=["root"],
    responses={404: {"description": "Not found"}},
)


@root_router.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


if cfg.telegram.mode == "webhook":

    @root_router.post(cfg.telegram.webhook_path)
    async def bot_webhook(
        update: dict, x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None
    ) -> None | dict:
        """Register webhook endpoint for telegram bot"""
        if x_telegram_bot_api_secret_token != cfg.telegram.bot_token.get_secret_value():
            logger.error("Wrong secret token !")
            return {"status": "error", "message": "Wrong secret token !"}
        telegram_update = types.Update(**update)
        await dp.feed_webhook_update(bot=bot, update=telegram_update)
