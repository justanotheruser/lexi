from sqlalchemy.ext.asyncio import AsyncSession

from app.features.users.models import User


async def get_or_create_user(session: AsyncSession, user: User):
    pass
