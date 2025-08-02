"""I18n middleware that provides synchronous translation interface"""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.telegram.i18n import I18nService


class I18nMiddleware(BaseMiddleware):
    """Middleware that provides synchronous i18n interface"""

    def __init__(self, i18n_service: I18nService):
        super().__init__()
        self.i18n_service = i18n_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Get user ID from the event
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            data["i18n"] = await self.i18n_service.get_i18n(user_id)

        return await handler(event, data)
