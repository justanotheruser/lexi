from aiogram import F
from aiogram.types import Message, User

from app.adapters.repo.user_repo import SQLModelUserRepo
from app.features.story_creator.service import StoryCreatorService
from app.features.users.user_cache import UserCache
from app.telegram.bot import telegram_router
from app.telegram.i18n import I18nManager


@telegram_router.message(F.text == "/start")
async def handle_start_command(
    message: Message, user_cache: UserCache, sessionmaker, i18n: I18nManager
) -> None:
    """""Get user settings and ask user for story language selection""" ""
    tg_user: User = message.from_user  # type: ignore[assignment]

    if (user := await user_cache.get(tg_user.id)) is None:
        session = sessionmaker()
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


@telegram_router.message(F.text)
async def handle_language_selection(
    message: Message, i18n: I18nManager, story_creator: StoryCreatorService
) -> None:
    """Handle language selection from user input"""
    if message.from_user is None or message.text is None:
        return
    user_input = message.text.strip()
    # Find the best matching language
    language_code, _ = story_creator.find_best_language_match(
        user_input,
        i18n.language,
    )

    if language_code:
        # Language found - send confirmation
        # Get language name in user's native language
        language_name_in_user_lang = story_creator.get_language_name_in_user_language(
            language_code, i18n.language
        )

        # Get confirmation message in user's language (synchronous)
        confirmation_message = i18n["LETS_LEARN"].translate(
            language_name=language_name_in_user_lang
        )

        # TODO: add phrase in the language of story later
        # learning_phrase = get_learning_phrase_in_target_language(language_code)
        # Combine messages
        # response = f"{confirmation_message}\n\n{learning_phrase}"

        await message.reply(confirmation_message)
    else:
        # Language not supported
        error_message = i18n["LANGUAGE_NOT_SUPPORTED"].translate()
        await message.reply(error_message)
