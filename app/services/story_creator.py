from __future__ import annotations

from typing import TYPE_CHECKING

from openai import AsyncOpenAI

from app.models.dto.story_creation_params import StoryCreationParams
from app.services.base import BaseService
from app.services.crud.user import UserService

if TYPE_CHECKING:
    from app.config import AppConfig


class ContentModerationError(Exception):
    """Raised when content fails moderation checks"""


class StoryCreatorService(BaseService):
    """Service for story creation business logic"""

    def __init__(self, config: AppConfig, user_service: UserService) -> None:
        super().__init__()
        self.config = config
        self.user_service = user_service
        self.openai_client = AsyncOpenAI(
            api_key=config.content_moderation.openai_api_key.get_secret_value()
        )

    async def get_default_language_for_user(self, user_id: int) -> str | None:
        """Get the default language for story creation based on user's last story language"""
        user = await self.user_service.get(user_id)
        if not user or not user.use_last_story_language:
            return None

        return user.last_story_language_code

    async def update_user_language_preference(self, user_id: int, language_code: str) -> None:
        """Update user's last story language preference"""
        user = await self.user_service.get(user_id)
        if user and user.last_story_language_code != language_code:
            await self.user_service.update(
                user=user,
                last_story_language_code=language_code,
                use_last_story_language=True,
            )

    async def validate_content_moderation(self, text: str) -> bool:
        """
        Validate text content using OpenAI Moderation API.
        Returns True if content is appropriate, False otherwise.
        """
        # If content moderation is disabled, always return True
        if not self.config.content_moderation.is_enabled:
            return True

        try:
            response = await self.openai_client.moderations.create(input=text)
            result = response.results[0]

            # Check for any flagged categories
            if result.flagged:
                self.logger.warning("Content flagged by moderation API: %s", text)
                return False

            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error("Error during content moderation: %s", e)
            # In case of API error, be conservative and reject
            return False

    async def validate_protagonist(self, protagonist: str) -> bool:
        """Validate protagonist description for PG-13 content"""
        return await self.validate_content_moderation(protagonist)

    async def validate_setting(self, setting: str) -> bool:
        """Validate setting description for PG-13 content"""
        return await self.validate_content_moderation(setting)

    async def create_story_params(
        self,
        user_id: int,
        target_language_code: str,
        protagonist: str,
        setting: str,
        native_language_code: str,
    ) -> StoryCreationParams:
        """
        Create story parameters with validation.
        Considers story parameters to be validated by the caller.
        """

        # Update user's language preference
        await self.update_user_language_preference(user_id, target_language_code)

        return StoryCreationParams(
            target_language_code=target_language_code,
            protagonist=protagonist,
            setting=setting,
            native_language_code=native_language_code,
        )

    def get_available_languages(self) -> list[str]:
        """Get list of available languages for story creation"""
        return self.config.story_teller.available_languages

    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language code is supported"""
        return language_code in self.config.story_teller.available_languages
