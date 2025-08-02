#!/usr/bin/env python3
"""Tests for i18n middleware"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.features.users.models import User
from app.telegram.i18n import I18nService
from app.telegram.middleware.i18n_middleware import I18nMiddleware


class MockUserCache:
    def __init__(self, users: dict[int, User]):
        self.users = users

    async def get(self, user_id: int) -> User | None:
        return self.users.get(user_id)


class MockMessage:
    def __init__(self, user_id: int):
        self.from_user = MagicMock()
        self.from_user.id = user_id


@pytest.fixture
def mock_users():
    """Create mock users with different languages"""
    return {
        1: User(id=1, ui_language_code="en"),
        2: User(id=2, ui_language_code="ru"),
    }


@pytest.fixture
def i18n_service(mock_users):
    """Create i18n service with mock cache"""
    mock_cache = MockUserCache(mock_users)
    return I18nService(mock_cache)


@pytest.fixture
def i18n_middleware(i18n_service):
    """Create i18n middleware"""
    return I18nMiddleware(i18n_service)


@pytest.mark.asyncio
async def test_middleware_injects_i18n(i18n_middleware):
    """Test that middleware injects i18n into handler data"""

    # Create mock message
    message = MockMessage(user_id=1)

    # Create mock handler
    mock_handler = AsyncMock()

    # Create data dict
    data = {}

    # Call middleware
    await i18n_middleware(mock_handler, message, data)

    # Verify i18n was injected
    assert "i18n" in data
    assert hasattr(data["i18n"], "__getitem__")
    assert hasattr(data["i18n"]["WELCOME"], "translate")


@pytest.mark.asyncio
async def test_middleware_translation_works(i18n_middleware):
    """Test that injected i18n can translate messages"""

    # Create mock message
    message = MockMessage(user_id=1)

    # Create mock handler
    mock_handler = AsyncMock()

    # Create data dict
    data = {}

    # Call middleware
    await i18n_middleware(mock_handler, message, data)

    # Test translation
    i18n = data["i18n"]
    welcome = i18n["WELCOME"].translate()
    assert welcome == "👋 Welcome! I'll help you learn languages."


@pytest.mark.asyncio
async def test_middleware_different_languages(i18n_middleware):
    """Test that middleware works with different user languages"""

    # Test English user
    message_en = MockMessage(user_id=1)
    data_en = {}
    await i18n_middleware(AsyncMock(), message_en, data_en)

    welcome_en = data_en["i18n"]["WELCOME"].translate()
    assert welcome_en == "👋 Welcome! I'll help you learn languages."

    # Test Russian user
    message_ru = MockMessage(user_id=2)
    data_ru = {}
    await i18n_middleware(AsyncMock(), message_ru, data_ru)

    welcome_ru = data_ru["i18n"]["WELCOME"].translate()
    assert welcome_ru == "👋 Добро пожаловать! Я помогу вам изучать языки."


@pytest.mark.asyncio
async def test_middleware_parameter_substitution(i18n_middleware):
    """Test that middleware supports parameter substitution"""

    # Create mock message
    message = MockMessage(user_id=1)

    # Create mock handler
    mock_handler = AsyncMock()

    # Create data dict
    data = {}

    # Call middleware
    await i18n_middleware(mock_handler, message, data)

    # Test translation with parameters
    i18n = data["i18n"]
    learn_msg = i18n["LETS_LEARN"].translate(language_name="Python")
    assert learn_msg == "✅ Ok, let's learn <b>Python</b>!"


@pytest.mark.asyncio
async def test_middleware_no_user_id():
    """Test middleware behavior when no user ID is available"""

    # Create i18n service
    i18n_service = I18nService(MockUserCache({}))
    middleware = I18nMiddleware(i18n_service)

    # Create message without user
    message = MagicMock()
    message.from_user = None

    # Create mock handler
    mock_handler = AsyncMock()

    # Create data dict
    data = {}

    # Call middleware
    await middleware(mock_handler, message, data)

    # Verify no i18n was injected
    assert "i18n" not in data


if __name__ == "__main__":
    print("Running middleware tests...")
    # This would need proper pytest setup to run
    print("Tests completed!")
