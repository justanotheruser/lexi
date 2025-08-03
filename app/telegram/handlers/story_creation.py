from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from pydantic import ValidationError

from app.models.dto.story_creation_params import StoryCreationParams
from app.services.story_teller import StoryTellerService
from app.telegram.keyboards.callback_data.menu import CDMenu, CDStoryBack, CDStoryLanguageSelect
from app.telegram.keyboards.callback_data.story import CDStoryChoice, CDVocabularyWord
from app.telegram.keyboards.common import back_keyboard

if TYPE_CHECKING:
    from app.config import AppConfig
    from app.models.dto.user import UserDto


class StoryCreationStates(StatesGroup):
    """FSM states for story creation dialog"""

    selecting_language = State()
    defining_protagonist = State()
    defining_setting = State()


router: Final[Router] = Router(name="story_creation")
logger: Final[logging.Logger] = logging.getLogger(__name__)


@router.callback_query(CDStoryLanguageSelect.filter())
async def handle_story_language_selection(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: I18nContext,
    config: AppConfig,
) -> Any:
    """Handle story language selection from inline keyboard"""
    if not callback.data:
        return

    # Extract language code from callback data
    language_code = callback.data.split(":")[1] if ":" in callback.data else None

    if not language_code or language_code not in config.story_teller.available_languages:
        await callback.answer(i18n.messages.language_not_supported())
        return

    # Store selected language
    await state.update_data(target_language_code=language_code)

    # Get language name in user's language
    language_name = getattr(i18n.messages, language_code, lambda: language_code.upper())()

    # Confirm selection and ask for protagonist
    confirmation_text = i18n.messages.language_selected(language=language_name)
    protagonist_text = i18n.messages.define_protagonist()
    response_text = f"{confirmation_text}\n\n{protagonist_text}"

    await callback.message.edit_text(
        text=response_text,
        reply_markup=back_keyboard(i18n=i18n, data=CDStoryBack()),
    )
    await state.set_state(StoryCreationStates.defining_protagonist)


@router.message(StoryCreationStates.defining_protagonist, F.text)
async def handle_protagonist_input(
    message: Message,
    state: FSMContext,
    i18n: I18nContext,
) -> Any:
    """Handle protagonist definition input"""
    if not message.text:
        return

    user_input = message.text.strip()

    # Store protagonist
    await state.update_data(protagonist=user_input)

    # Ask for setting
    setting_text = i18n.messages.define_setting()

    await message.reply(
        text=setting_text,
        reply_markup=back_keyboard(i18n=i18n, data=CDStoryBack()),
    )
    await state.set_state(StoryCreationStates.defining_setting)


@router.message(StoryCreationStates.defining_setting, F.text)
async def handle_setting_input(
    message: Message,
    state: FSMContext,
    i18n: I18nContext,
    story_teller: StoryTellerService,
) -> Any:
    """Handle setting definition input"""
    if not message.text or not message.from_user:
        return

    # TODO: validate user input
    user_input = message.text.strip()

    await state.update_data(setting=user_input)
    data = await state.get_data()

    try:
        story_creation_params = StoryCreationParams(
            target_language_code=data["target_language_code"],
            protagonist=data["protagonist"],
            setting=data["setting"],
            native_language_code=i18n.locale,
        )
    except (ValidationError, KeyError) as e:
        logger.error("Story creation failed: %s", e)
        await message.reply(i18n.messages.invalid_input())
        return

    confirmation_text = i18n.messages.story_setup_complete()
    await message.reply(confirmation_text)

    # Create story session
    session = await story_teller.create_story_session(message.from_user.id, story_creation_params)

    # Generate initial story
    story_bit = await story_teller.generate_initial_story(session)

    # Format story text with key words
    formatted_text = story_teller.format_story_text_with_key_words(
        story_bit.text, story_bit.key_words
    )

    # Create keyboard with choices and vocabulary words
    keyboard_builder = InlineKeyboardBuilder()

    # Add story choices
    for choice in story_bit.choices:
        keyboard_builder.button(
            text=choice.text, callback_data=CDStoryChoice(choice_id=choice.choice_id)
        )

    # Add vocabulary word buttons
    for word in story_bit.key_words:
        keyboard_builder.button(text=f"📖 {word}", callback_data=CDVocabularyWord(word=word))

    # Arrange buttons: choices in one row, vocabulary words in another
    keyboard_builder.adjust(1, len(story_bit.key_words))

    await message.reply(
        text=formatted_text,
        reply_markup=keyboard_builder.as_markup(),
    )

    # Clear the FSM state
    await state.clear()


@router.callback_query(CDStoryBack.filter())
async def handle_story_back(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: I18nContext,
    config: AppConfig,
) -> Any:
    """Handle back button in story creation flow"""
    current_state = await state.get_state()

    if current_state == StoryCreationStates.selecting_language.state:
        # Go back to main menu
        await callback.message.edit_text(
            text=i18n.messages.greeting(
                name=callback.from_user.full_name if callback.from_user else "User"
            ),
            reply_markup=back_keyboard(i18n=i18n, data=CDMenu()),
        )
        await state.clear()
    elif current_state == StoryCreationStates.defining_protagonist.state:
        # Go back to language selection
        await show_language_selection(callback, i18n, config)
        await state.set_state(StoryCreationStates.selecting_language)
    elif current_state == StoryCreationStates.defining_setting.state:
        # Go back to protagonist definition
        await callback.message.edit_text(
            text=i18n.messages.define_protagonist(),
            reply_markup=back_keyboard(i18n=i18n, data=CDStoryBack()),
        )
        await state.set_state(StoryCreationStates.defining_protagonist)


async def show_language_selection(
    callback: CallbackQuery,
    i18n: I18nContext,
    config: AppConfig,
) -> None:
    """Show language selection keyboard for story creation"""
    keyboard_builder = InlineKeyboardBuilder()

    # Add language buttons
    for lang_code in config.story_teller.available_languages:
        lang_name = getattr(i18n.messages, lang_code, lambda: lang_code.upper())()
        keyboard_builder.button(
            text=lang_name, callback_data=CDStoryLanguageSelect(language_code=lang_code)
        )

    # Add back button
    keyboard_builder.button(text=i18n.buttons.back(), callback_data=CDStoryBack())

    # Arrange buttons in a 3-column grid
    keyboard_builder.adjust(3)

    await callback.message.edit_text(
        text=i18n.messages.select_story_language(),
        reply_markup=keyboard_builder.as_markup(),
    )
