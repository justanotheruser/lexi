from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram_i18n import I18nContext

from lexi.telegram.keyboards.callback_data.menu import (
    CDLanguageSelect,
    CDMenu,
    CDShowLanguages,
    CDStoryLanguageSelect,
)
from lexi.telegram.keyboards.common import back_keyboard
from lexi.telegram.keyboards.menu import (
    language_keyboard,
    language_selection_keyboard,
    main_menu_keyboard,
    story_language_selection_keyboard,
)

if TYPE_CHECKING:
    from lexi.config import AppConfig
    from lexi.models.dto.user import UserDto
    from lexi.services.crud.user import UserService
    from lexi.services.story_creator import StoryCreatorService
    from lexi.telegram.helpers import MessageHelper

router: Final[Router] = Router(name=__name__)


@router.message(CommandStart())
@router.callback_query(CDMenu.filter())
async def greeting(
    _: TelegramObject,
    helper: MessageHelper,
    i18n: I18nContext,
    user: UserDto,
) -> Any:
    return await helper.answer(
        text=i18n.messages.greeting(name=user.mention),
        reply_markup=main_menu_keyboard(i18n=i18n),
    )


@router.message(Command("language"))
async def language_command(
    _: TelegramObject,
    helper: MessageHelper,
    i18n: I18nContext,
) -> Any:
    return await helper.answer(
        text=i18n.messages.language_select(),
        reply_markup=language_keyboard(i18n=i18n),
    )


@router.message(Command("story_language"))
async def story_language_command(
    _: TelegramObject,
    helper: MessageHelper,
    i18n: I18nContext,
    story_creator: StoryCreatorService,
) -> Any:
    return await helper.answer(
        text=i18n.messages.story_language_select(),
        reply_markup=story_language_selection_keyboard(
            available_languages=story_creator.get_available_languages(), i18n=i18n
        ),
    )


@router.callback_query(CDShowLanguages.filter())
async def show_languages(
    _: TelegramObject,
    helper: MessageHelper,
    i18n: I18nContext,
    config: AppConfig,
) -> Any:
    return await helper.answer(
        text=i18n.messages.available_ui_language(),
        reply_markup=language_selection_keyboard(locales=config.telegram.locales, i18n=i18n),
    )


@router.callback_query(CDLanguageSelect.filter())
async def select_language(
    callback: CallbackQuery,
    helper: MessageHelper,
    i18n: I18nContext,
    user: UserDto,
    user_service: UserService,
) -> Any:
    if not callback.data:
        return
    split_data = callback.data.split(":")
    if len(split_data) < 2:
        return
    language_code = split_data[1]

    # Update user's language in the database
    updated_user = await user_service.update(user=user, language=language_code)

    if updated_user:
        await helper.answer(
            text=i18n.messages.language_changed(language=language_code),
            reply_markup=back_keyboard(i18n=i18n),
        )
    else:
        await helper.answer(
            text=i18n.messages.language_not_supported(),
            reply_markup=language_keyboard(i18n=i18n),
        )


@router.callback_query(CDStoryLanguageSelect.filter())
async def select_story_language(
    callback: CallbackQuery,
    helper: MessageHelper,
    i18n: I18nContext,
    user: UserDto,
    user_service: UserService,
    story_creator: StoryCreatorService,
) -> Any:
    """Handle story language selection"""
    if not callback.data:
        return

    # Extract language code from callback data
    language_code = callback.data.split(":")[1] if ":" in callback.data else None

    if not language_code or not story_creator.is_language_supported(language_code):
        await helper.answer(
            text=i18n.messages.story_language_not_supported(),
            reply_markup=story_language_selection_keyboard(
                available_languages=story_creator.get_available_languages(), i18n=i18n
            ),
        )
        return

    # Update user's story language in the database
    updated_user = await user_service.update(user=user, story_language_code=language_code)

    if updated_user:
        await helper.answer(
            text=i18n.messages.story_language_changed(language=language_code),
            reply_markup=back_keyboard(i18n=i18n),
        )
    else:
        await helper.answer(
            text=i18n.messages.story_language_not_supported(),
            reply_markup=story_language_selection_keyboard(
                available_languages=story_creator.get_available_languages(), i18n=i18n
            ),
        )


# Handle manual language code input with a specific filter for 2-letter codes
@router.message(F.text.len() == 2, F.text.regexp(r"^[a-zA-Z]{2}$"))
async def handle_language_input(
    message: Message,
    helper: MessageHelper,
    i18n: I18nContext,
    user: UserDto,
    user_service: UserService,
    config: AppConfig,
) -> Any:
    # Handle manual language code input (2-letter codes)
    if not message.text:
        return
    text = message.text.strip().lower()

    # Supported language codes from config
    supported_languages = set(config.telegram.locales)

    if text in supported_languages:
        # Update user's language in the database
        updated_user = await user_service.update(user=user, language=text)

        if updated_user:
            await helper.answer(
                text=i18n.messages.language_changed(language=text),
                reply_markup=back_keyboard(i18n=i18n),
            )
        else:
            await helper.answer(
                text=i18n.messages.language_not_supported(),
                reply_markup=language_keyboard(i18n=i18n),
            )
    else:
        await helper.answer(
            text=i18n.messages.language_not_supported(),
            reply_markup=language_keyboard(i18n=i18n),
        )
