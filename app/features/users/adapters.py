from app.features.users.domain.models import User
from app.features.users.ports import UserCache


class InMemoryUserCahce(UserCache):
    """For tests and debugging"""

    def __init__(self) -> None:
        self._cache = {}

    async def save(self, user: User) -> None:
        self._cache[user.id] = user

    async def get(self, user_id: int) -> User | None:
        return self._cache.get(user_id)
