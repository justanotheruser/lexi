from sqlalchemy.ext.asyncio import AsyncSession

from app.features.users.models import User
from app.features.users.user_repo import UserRepo


class SQLModelUserRepo(UserRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_or_create_user(self, user_id: int, current_language_code: str) -> User:
        user = await self.session.get(User, user_id)
        if user is None:
            user = User(id=user_id, ui_language_code=current_language_code)
            self.session.add(user)
            await self.session.commit()
        return user
