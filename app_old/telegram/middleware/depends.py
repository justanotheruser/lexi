from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


def depends(arg_name: str, arg_value: Any):
    """Creates middleware that injects dependency"""

    class AddDependencyMiddleware(BaseMiddleware):
        name = arg_name
        value = arg_value

        async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
        ) -> Any:
            data[self.name] = self.value
            return await handler(event, data)

    return AddDependencyMiddleware()
