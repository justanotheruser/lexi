from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from app.adapters.repo.user_repo import SQLModelUserRepo
from app.features.users.user_cache import UserCache
from app.telegram.handlers.story_creation import StoryCreationStates
from app.telegram.i18n import I18nManager

start_router = Router(name="start")


@start_router.message(F.text == "/start")
async def handle_start_command(
    message: Message, user_cache: UserCache, sessionmaker, i18n: I18nManager, state: FSMContext
) -> None:
    """Get user settings and initiate story creation dialog"""
    tg_user: User = message.from_user  # type: ignore[assignment]

    if (user := await user_cache.get(tg_user.id)) is None:
        async with sessionmaker() as session:
            repo = SQLModelUserRepo(session)
            language_code = tg_user.language_code or "en"
            user = await repo.get_or_create_user(
                user_id=tg_user.id, current_language_code=language_code
            )
            await user_cache.save(user)

    # Get welcome message in user's language (synchronous)
    welcome_message = i18n["WELCOME"].translate()
    language_selection_message = i18n["WHAT_LANGUAGE_YOU_WANT_LEARN"].translate()

    response = f"{welcome_message}\n\n{language_selection_message}"
    await message.reply(response)

    # Start the story creation dialog
    await state.set_state(StoryCreationStates.selecting_language)
