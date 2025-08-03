from typing import Protocol

from app.features.users.models import User


class UserRepo(Protocol):
    async def get_or_create_user(self, user_id: int, current_language_code: str) -> User: ...
