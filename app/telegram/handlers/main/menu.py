from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Final

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from app.telegram.handlers.story_creation import StoryCreationStates, show_language_selection
from app.telegram.keyboards.callback_data.menu import (
    CDCreateStory,
    CDLanguageSelect,
    CDMenu,
    CDShowLanguages,
    CDStoryBack,
)
from app.telegram.keyboards.common import back_keyboard
from app.telegram.keyboards.menu import (
    language_keyboard,
    language_selection_keyboard,
    main_menu_keyboard,
)

if TYPE_CHECKING:
    from app.config import AppConfig
    from app.models.dto.user import UserDto
    from app.services.crud.user import UserService
    from app.telegram.helpers import MessageHelper

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


@router.callback_query(CDCreateStory.filter())
async def create_story(
    callback: CallbackQuery,
    helper: MessageHelper,
    i18n: I18nContext,
    state: FSMContext,
    config: AppConfig,
) -> Any:
    """Start story creation flow"""
    # Set initial state
    await state.set_state(StoryCreationStates.selecting_language)

    # Show language selection
    await show_language_selection(callback, i18n, config)

    return None


@router.message(Command("language"))
async def language_command(
    message: Message,
    helper: MessageHelper,
    i18n: I18nContext,
) -> Any:
    return await helper.answer(
        text=i18n.messages.language_select(),
        reply_markup=language_keyboard(i18n=i18n),
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
