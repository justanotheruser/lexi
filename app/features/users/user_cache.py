import json

from app.features.users.models import User
from app.ports.cache import Cache


class UserCache:
    namespace = "users:user:"

    def __init__(self, cache: Cache) -> None:
        self._cache = cache

    async def save(self, user: User, ttl: int = 24 * 60 * 60) -> None:
        key = self.namespace + str(user.id)
        await self._cache.set(key, json.dumps(user), ttl=ttl)

    async def get(self, user_id: int) -> User | None:
        key = self.namespace + str(user_id)
        data = await self._cache.get(key)
        if data is None:
            return None
        return User(**json.loads(data))
