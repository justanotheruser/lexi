from __future__ import annotations

import logging
import traceback
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ErrorLoggerMiddleware(BaseMiddleware):
    """
    Middleware that intercepts and logs exceptions in aiogram handlers.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            # Log the exception with full traceback
            self.logger.error(
                "Exception in handler for event type %s: %s\nTraceback:\n%s",
                event.__class__.__name__,
                str(e),
                traceback.format_exc(),
            )

            # Re-raise the exception to maintain the original behavior
            raise
