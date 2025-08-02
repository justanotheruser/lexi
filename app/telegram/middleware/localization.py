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


from aiogram import BaseMiddleware
from aiogram.types import Message

DEFAULT_LANG = "en"


class LocalizationMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: Message, data: dict):
        user_id = message.from_user.id
        # Get user's language or default
        lang_code = user_language.get(user_id, DEFAULT_LANG)
        # Attach translator instance to message
        message.translator = TRANSLATORS.get(lang_code, TRANSLATORS[DEFAULT_LANG])
        data["translator"] = message.translator  # also available in handlers
