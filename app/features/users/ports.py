from typing import Protocol

from app.features.users.domain.models import User


class UserCache(Protocol):
    async def save(self, user: User) -> None: ...
    async def get(self, user_id: int) -> User | None: ...
