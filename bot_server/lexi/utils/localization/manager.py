from __future__ import annotations

from typing import TYPE_CHECKING, cast

from aiogram.types import User as AiogramUser
from aiogram_i18n.managers import BaseManager

from lexi.services.crud import UserService

if TYPE_CHECKING:
    from lexi.models.dto.user import UserDto


class UserManager(BaseManager):
    async def get_locale(
        self,
        event_from_user: AiogramUser | None = None,
        # user: Optional[UserDto] = None,
        user=None,
    ) -> str:
        locale: str | None = None
        if user is not None:
            locale = user.language
        elif event_from_user is not None and event_from_user.language_code is not None:
            locale = event_from_user.language_code
        return locale or cast(str, self.default_locale)

    async def set_locale(self, locale: str, user: UserDto, user_service: UserService) -> None:
        await user_service.update(user=user, language=locale)
