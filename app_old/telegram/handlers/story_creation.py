import json
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, User
from loguru import logger

from app.features.content_moderation.service import ContentModerationService
from app.features.story_creator.service import StoryCreatorService
from app.telegram.i18n import I18nManager


class StoryCreationStates(StatesGroup):
    """FSM states for story creation dialog"""

    selecting_language = State()
    defining_protagonist = State()
    defining_setting = State()


story_creation_router = Router(name="story_creation")


@story_creation_router.message(F.text)
async def handle_language_selection(
    message: Message,
    state: FSMContext,
    i18n: I18nManager,
    story_creator: StoryCreatorService,
) -> None:
    """Handle language selection from user input"""
    if message.from_user is None or message.text is None:
        return

    current_state = await state.get_state()

    # If we're not in a story creation state, ignore this message
    if current_state is None:
        return

    user_input = message.text.strip()

    if current_state == StoryCreationStates.selecting_language.state:
        await handle_language_input(message, state, user_input, i18n, story_creator)
    elif current_state == StoryCreationStates.defining_protagonist.state:
        await handle_protagonist_input(message, state, user_input, i18n)
    elif current_state == StoryCreationStates.defining_setting.state:
        await handle_setting_input(message, state, user_input, i18n)


async def handle_language_input(
    message: Message,
    state: FSMContext,
    user_input: str,
    i18n: I18nManager,
    story_creator: StoryCreatorService,
) -> None:
    """Handle language selection input"""
    # Find the best matching language
    language_code, confidence = story_creator.find_best_language_match(
        user_input,
        i18n.language,
    )

    if language_code and confidence >= 70:
        # Language found - store it and move to protagonist
        await state.update_data(target_language_code=language_code)

        # Get language name in user's native language
        language_name_in_user_lang = story_creator.get_language_name_in_user_language(
            language_code, i18n.language
        )

        # Get confirmation message
        confirmation_message = i18n["LANGUAGE_SELECTED"].translate(
            language_name=language_name_in_user_lang
        )

        # Ask for protagonist
        protagonist_message = i18n["DEFINE_PROTAGONIST"].translate()
        response = f"{confirmation_message}\n\n{protagonist_message}"

        await message.reply(response)
        await state.set_state(StoryCreationStates.defining_protagonist)
    else:
        # Language not supported
        error_message = i18n["LANGUAGE_NOT_SUPPORTED"].translate()
        await message.reply(error_message)


async def handle_protagonist_input(
    message: Message,
    state: FSMContext,
    user_input: str,
    i18n: I18nManager,
) -> None:
    """Handle protagonist definition input"""
    # Check content moderation
    moderation_service = ContentModerationService()
    is_appropriate = await moderation_service.check_content_appropriateness(user_input)

    if is_appropriate:
        await state.update_data(protagonist=user_input)

        # Ask for setting
        setting_message = i18n["DEFINE_SETTING"].translate()
        await message.reply(setting_message)
        await state.set_state(StoryCreationStates.defining_setting)
    else:
        # Content flagged as inappropriate
        error_message = i18n["CONTENT_INAPPROPRIATE"].translate()
        await message.reply(error_message)


async def handle_setting_input(
    message: Message,
    state: FSMContext,
    user_input: str,
    i18n: I18nManager,
) -> None:
    """Handle setting definition input"""
    # Check content moderation
    moderation_service = ContentModerationService()
    is_appropriate = await moderation_service.check_content_appropriateness(user_input)

    if is_appropriate:
        await state.update_data(setting=user_input)

        # Get all story parameters
        data = await state.get_data()

        # Create story parameters JSON
        story_params = {
            "target_language_code": data.get("target_language_code"),
            "protagonist": data.get("protagonist"),
            "setting": data.get("setting"),
        }

        # Send confirmation with JSON
        confirmation_message = i18n["STORY_PARAMETERS_READY"].translate()
        json_message = (
            f"{confirmation_message}\n\n```json\n{json.dumps(story_params, indent=2)}\n```"
        )

        await message.reply(json_message)

        # Clear the FSM state
        await state.clear()
    else:
        # Content flagged as inappropriate
        error_message = i18n["CONTENT_INAPPROPRIATE"].translate()
        await message.reply(error_message)
