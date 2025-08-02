from aiogram import F
from aiogram.types import Message, User

from app.adapters.repo.user_repo import SQLModelUserRepo
from app.features.users.user_cache import UserCache
from app.telegram.bot import telegram_router
from app.telegram.i18n import I18nManager
from app.telegram.middlewares import (
    setup_cache_middlewares,
    setup_i18n_middleware,
    setup_sessionmaker_middleware,
)
from app.utils.language import (
    find_best_language_match,
    get_language_confirmation_message,
    get_language_name_in_user_language,
    get_language_not_supported_message,
    get_learning_phrase_in_target_language,
)


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
async def handle_language_selection(message: Message, i18n: I18nManager) -> None:
    """Handle language selection from user input"""
    if message.from_user is None or message.text is None:
        return
    user_input = message.text.strip()
    # Find the best matching language
    language_code, _ = find_best_language_match(
        user_input,
        cfg.language.supported_languages,
        i18n.language,
        cfg.language.supported_languages_in_user_language,
    )

    if language_code:
        # Language found - send confirmation
        # Get language name in user's native language
        language_name_in_user_lang = get_language_name_in_user_language(
            language_code, i18n.language, cfg.language.supported_languages_in_user_language
        )

        # Get confirmation message in user's language (synchronous)
        confirmation_message = i18n["LETS_LEARN"].translate(
            language_name=language_name_in_user_lang
        )

        # Get learning phrase in target language
        learning_phrase = get_learning_phrase_in_target_language(language_code)

        # Combine messages
        response = f"{confirmation_message}\n\n{learning_phrase}"
        await message.reply(response)
    else:
        # Language not supported
        error_message = i18n["LANGUAGE_NOT_SUPPORTED"].translate()
        await message.reply(error_message)
