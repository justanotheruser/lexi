from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Language


async def load_language_data(session: AsyncSession):
    """Load language data from database and return as dictionaries"""
    result = await session.execute(select(Language))
    language_records = result.scalars().all()

    supported_languages = {}
    supported_languages_in_user_language = {}

    for record in language_records:
        # For supported_languages, we want where language_code == user_language_code
        if record.language_code == record.user_language_code:
            supported_languages[record.language_code] = record.word

        # For supported_languages_in_user_language, group by user_language_code
        if record.user_language_code not in supported_languages_in_user_language:
            supported_languages_in_user_language[record.user_language_code] = {}
        supported_languages_in_user_language[record.user_language_code][
            record.language_code
        ] = record.word

    return supported_languages, supported_languages_in_user_language
