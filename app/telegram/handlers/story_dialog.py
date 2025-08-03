from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from app.services.story_teller import StoryTellerService
from app.telegram.keyboards.callback_data.story import CDStoryChoice, CDStoryEnd, CDVocabularyWord

if TYPE_CHECKING:
    from app.config import AppConfig
    from app.models.dto.user import UserDto

logger: Final[logging.Logger] = logging.getLogger(__name__)

router: Final[Router] = Router(name="story_dialog")


@router.callback_query(CDStoryChoice.filter())
async def handle_story_choice(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: I18nContext,
    story_teller: StoryTellerService,
) -> Any:
    """Handle story choice selection"""
    if not callback.data or not callback.from_user:
        return

    choice_data = CDStoryChoice.unpack(callback.data)
    choice_id = choice_data.choice_id

    # Get story session
    session = await story_teller.get_story_session(callback.from_user.id)
    if not session:
        await callback.answer(i18n.messages.story_session_expired())
        return

    # Find the selected choice
    if not session.choices or int(choice_id) > len(session.choices):
        await callback.answer(i18n.messages.invalid_choice())
        return

    selected_choice = session.choices[int(choice_id) - 1]

    # Continue the story
    try:
        story_bit = await story_teller.continue_story(session, selected_choice)

        # Format story text with key words
        formatted_text = story_teller.format_story_text_with_key_words(
            story_bit.text, story_bit.key_words
        )

        # Create keyboard
        keyboard_builder = InlineKeyboardBuilder()

        # Add story choices
        for choice in story_bit.choices:
            keyboard_builder.button(
                text=choice.text, callback_data=CDStoryChoice(choice_id=choice.choice_id)
            )

        # Add vocabulary word buttons
        for word in story_bit.key_words:
            keyboard_builder.button(text=f"📖 {word}", callback_data=CDVocabularyWord(word=word))

        # Check if story is complete (no more choices)
        if not story_bit.choices:
            keyboard_builder.button(text=i18n.buttons.end_story(), callback_data=CDStoryEnd())

        # Arrange buttons
        keyboard_builder.adjust(1, len(story_bit.key_words))

        await callback.message.edit_text(  # type: ignore
            text=formatted_text,
            reply_markup=keyboard_builder.as_markup(),
        )

    except Exception as e:
        logger.error(f"Error continuing story: {e}")
        await callback.answer(i18n.messages.story_generation_error())


@router.callback_query(CDVocabularyWord.filter())
async def handle_vocabulary_word(
    callback: CallbackQuery,
    i18n: I18nContext,
    story_teller: StoryTellerService,
) -> Any:
    """Handle vocabulary word lookup"""
    if not callback.data or not callback.from_user:
        return

    vocab_data = CDVocabularyWord.unpack(callback.data)
    word = vocab_data.word

    # Get story session for context
    session = await story_teller.get_story_session(callback.from_user.id)
    if not session:
        await callback.answer(i18n.messages.story_session_expired())
        return

    try:
        # Get vocabulary definition
        vocab_word = await story_teller.get_vocabulary_definition(
            word=word,
            target_language=session.params.target_language_code,
            native_language=session.params.native_language_code,
            context=session.story_text,
        )

        # Create alert text
        alert_text = f"📖 <b>{word}</b>\n\n"
        alert_text += f"<b>Definition:</b> {vocab_word.definition}\n"
        alert_text += f"<b>Translation:</b> {vocab_word.translation}"

        await callback.answer(
            text=alert_text,
            show_alert=True,
        )

    except Exception as e:
        logger.error(f"Error getting vocabulary definition: {e}")
        await callback.answer(i18n.messages.vocabulary_error())


@router.callback_query(CDStoryEnd.filter())
async def handle_story_end(
    callback: CallbackQuery,
    i18n: I18nContext,
    story_teller: StoryTellerService,
) -> Any:
    """Handle story completion"""
    if not callback.from_user:
        return

    # Get story session
    session = await story_teller.get_story_session(callback.from_user.id)
    if not session:
        await callback.answer(i18n.messages.story_session_expired())
        return

    # TODO: In future, trigger image generation here
    # For now, just show completion message
    completion_text = i18n.messages.story_completed()
    completion_text += f"\n\n📚 <b>Your Story:</b>\n{session.story_text}"

    # Create keyboard to go back to main menu
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text=i18n.buttons.back_to_menu(), callback_data="menu")

    await callback.message.edit_text(  # type: ignore
        text=completion_text,
        reply_markup=keyboard_builder.as_markup(),
    )

    # Clean up session
    await story_teller.delete_story_session(callback.from_user.id)
