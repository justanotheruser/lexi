#!/usr/bin/env python3
"""
Tests for the StoryCreatorService
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.dto.story_creation_params import StoryCreationParams
from app.services.story_creator import ContentModerationError, StoryCreatorService


@pytest.mark.asyncio
async def test_story_creator_service_initialization():
    """Test that StoryCreatorService can be initialized"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True
    config.story_teller.available_languages = ["en", "es", "ru"]

    user_service = MagicMock()

    service = StoryCreatorService(config=config, user_service=user_service)

    assert service.config == config
    assert service.user_service == user_service


@pytest.mark.asyncio
async def test_is_language_supported():
    """Test language support checking"""
    config = MagicMock()
    config.story_teller.available_languages = ["en", "es", "ru"]

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    assert service.is_language_supported("en") is True
    assert service.is_language_supported("es") is True
    assert service.is_language_supported("ru") is True
    assert service.is_language_supported("fr") is False
    assert service.is_language_supported("invalid") is False


@pytest.mark.asyncio
async def test_get_available_languages():
    """Test getting available languages"""
    config = MagicMock()
    config.story_teller.available_languages = ["en", "es", "ru"]

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    languages = service.get_available_languages()
    assert languages == ["en", "es", "ru"]


@pytest.mark.asyncio
async def test_content_moderation_success():
    """Test successful content moderation"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    # Mock OpenAI moderation response
    mock_response = MagicMock()
    mock_result = MagicMock()
    mock_result.flagged = False
    mock_response.results = [mock_result]

    service.openai_client.moderations.create = AsyncMock(return_value=mock_response)

    result = await service.validate_content_moderation("A friendly cat")
    assert result is True


@pytest.mark.asyncio
async def test_content_moderation_failure():
    """Test failed content moderation"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    # Mock OpenAI moderation response
    mock_response = MagicMock()
    mock_result = MagicMock()
    mock_result.flagged = True
    mock_response.results = [mock_result]

    service.openai_client.moderations.create = AsyncMock(return_value=mock_response)

    result = await service.validate_content_moderation("Inappropriate content")
    assert result is False


@pytest.mark.asyncio
async def test_content_moderation_disabled():
    """Test content moderation when disabled"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = False

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    # Should return True regardless of content when disabled
    result = await service.validate_content_moderation("Any content, even inappropriate")
    assert result is True


@pytest.mark.asyncio
async def test_content_moderation_api_error():
    """Test content moderation when API throws an error"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    # Mock OpenAI to throw an exception
    service.openai_client.moderations.create = AsyncMock(side_effect=Exception("API Error"))

    # Should return False (conservative approach) when API fails
    result = await service.validate_content_moderation("Any content")
    assert result is False


@pytest.mark.asyncio
async def test_create_story_params_success():
    """Test successful story parameter creation"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True

    user_service = MagicMock()
    user_service.get = AsyncMock(return_value=None)  # No existing user
    user_service.update = AsyncMock()

    service = StoryCreatorService(config=config, user_service=user_service)

    params = await service.create_story_params(
        user_id=123,
        target_language_code="en",
        protagonist="A brave cat",
        setting="A magical forest",
        native_language_code="ru",
    )

    assert isinstance(params, StoryCreationParams)
    assert params.target_language_code == "en"
    assert params.protagonist == "A brave cat"
    assert params.setting == "A magical forest"
    assert params.native_language_code == "ru"

    # Verify user service was called to get user
    user_service.get.assert_called_once_with(123)
    # No update should be called since user doesn't exist
    user_service.update.assert_not_called()


@pytest.mark.asyncio
async def test_validate_protagonist_failure():
    """Test protagonist validation failure"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    # Mock OpenAI moderation response for flagged content
    mock_response = MagicMock()
    mock_result = MagicMock()
    mock_result.flagged = True
    mock_response.results = [mock_result]

    service.openai_client.moderations.create = AsyncMock(return_value=mock_response)

    result = await service.validate_protagonist("Inappropriate protagonist")
    assert result is False


@pytest.mark.asyncio
async def test_validate_setting_failure():
    """Test setting validation failure"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True

    user_service = MagicMock()
    service = StoryCreatorService(config=config, user_service=user_service)

    # Mock OpenAI moderation response for flagged content
    mock_response = MagicMock()
    mock_result = MagicMock()
    mock_result.flagged = True
    mock_response.results = [mock_result]

    service.openai_client.moderations.create = AsyncMock(return_value=mock_response)

    result = await service.validate_setting("Inappropriate setting")
    assert result is False


@pytest.mark.asyncio
async def test_create_story_params_with_existing_user():
    """Test story parameter creation with existing user that needs language update"""
    config = MagicMock()
    config.content_moderation.openai_api_key.get_secret_value.return_value = "test-key"
    config.content_moderation.is_enabled = True

    # Mock existing user with different language
    mock_user = MagicMock()
    mock_user.last_story_language_code = "es"
    mock_user.use_last_story_language = True

    user_service = MagicMock()
    user_service.get = AsyncMock(return_value=mock_user)
    user_service.update = AsyncMock()

    service = StoryCreatorService(config=config, user_service=user_service)

    params = await service.create_story_params(
        user_id=123,
        target_language_code="en",
        protagonist="A brave cat",
        setting="A magical forest",
        native_language_code="ru",
    )

    assert isinstance(params, StoryCreationParams)
    assert params.target_language_code == "en"
    assert params.protagonist == "A brave cat"
    assert params.setting == "A magical forest"
    assert params.native_language_code == "ru"

    # Verify user service was called to get user
    user_service.get.assert_called_once_with(123)
    # Verify user was updated with new language preference
    user_service.update.assert_called_once_with(
        user=mock_user,
        last_story_language_code="en",
        use_last_story_language=True,
    )
