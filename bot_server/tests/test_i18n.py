#!/usr/bin/env python3
"""Tests for i18n functionality"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.features.users.models import User
from app.telegram.i18n import I18nService, SyncI18nManager


class MockUserCache:
    def __init__(self, users: dict[int, User]):
        self.users = users

    async def get(self, user_id: int) -> User | None:
        return self.users.get(user_id)


@pytest.fixture
def mock_users():
    """Create mock users with different languages"""
    return {
        1: User(id=1, ui_language_code="en"),
        2: User(id=2, ui_language_code="ru"),
        3: User(id=3, ui_language_code="es"),
        4: User(id=4, ui_language_code="fr"),
        5: User(id=5, ui_language_code="de"),
    }


@pytest.fixture
def i18n_service(mock_users):
    """Create i18n service with mock cache"""
    mock_cache = MockUserCache(mock_users)
    return I18nService(mock_cache)


@pytest.mark.asyncio
async def test_user_language_detection(i18n_service, mock_users):
    """Test that user language is correctly detected"""

    # Test existing users
    assert await i18n_service.get_user_language(1) == "en"
    assert await i18n_service.get_user_language(2) == "ru"
    assert await i18n_service.get_user_language(3) == "es"

    # Test non-existent user (should return default)
    assert await i18n_service.get_user_language(999) == "en"


@pytest.mark.asyncio
async def test_translation_basic(i18n_service):
    """Test basic translation functionality"""

    # Test English user
    translator = await i18n_service.get_translator(1)
    assert translator.translate("WELCOME") == "👋 Welcome! I'll help you learn languages."

    # Test Russian user
    translator = await i18n_service.get_translator(2)
    assert translator.translate("WELCOME") == "👋 Добро пожаловать! Я помогу вам изучать языки."


@pytest.mark.asyncio
async def test_translation_with_parameters(i18n_service):
    """Test translation with parameter substitution"""

    # Test English user with parameters
    translator = await i18n_service.get_translator(1)
    result = translator.translate("LETS_LEARN", language_name="Python")
    assert result == "✅ Ok, let's learn <b>Python</b>!"

    # Test Russian user with parameters
    translator = await i18n_service.get_translator(2)
    result = translator.translate("LETS_LEARN", language_name="Python")
    assert result == "✅ Хорошо, давайте изучать <b>Python</b>!"


@pytest.mark.asyncio
async def test_sync_i18n_manager(i18n_service):
    """Test the synchronous i18n manager"""

    # Test English user
    translator = await i18n_service.get_translator(1)
    sync_i18n = SyncI18nManager(i18n_service, 1, translator)

    welcome = sync_i18n["WELCOME"].translate()
    assert welcome == "👋 Welcome! I'll help you learn languages."

    learn_msg = sync_i18n["LETS_LEARN"].translate(language_name="JavaScript")
    assert learn_msg == "✅ Ok, let's learn <b>JavaScript</b>!"


@pytest.mark.asyncio
async def test_all_supported_languages(i18n_service):
    """Test that all supported languages work correctly"""

    test_cases = [
        (1, "en", "👋 Welcome! I'll help you learn languages."),
        (2, "ru", "👋 Добро пожаловать! Я помогу вам изучать языки."),
        (3, "es", "👋 ¡Bienvenido! Te ayudaré a aprender idiomas."),
        (4, "fr", "👋 Bienvenue! Je vous aiderai à apprendre les langues."),
        (5, "de", "👋 Willkommen! Ich helfe Ihnen beim Sprachenlernen."),
    ]

    for user_id, expected_lang, expected_welcome in test_cases:
        translator = await i18n_service.get_translator(user_id)
        sync_i18n = SyncI18nManager(i18n_service, user_id, translator)

        welcome = sync_i18n["WELCOME"].translate()
        assert welcome == expected_welcome, f"Failed for user {user_id} ({expected_lang})"


@pytest.mark.asyncio
async def test_default_language_fallback(i18n_service):
    """Test that non-existent users get default language"""

    # Test non-existent user
    translator = await i18n_service.get_translator(999)
    sync_i18n = SyncI18nManager(i18n_service, 999, translator)

    welcome = sync_i18n["WELCOME"].translate()
    assert welcome == "👋 Welcome! I'll help you learn languages."


@pytest.mark.asyncio
async def test_unknown_translation_key(i18n_service):
    """Test that unknown keys return the key itself"""

    translator = await i18n_service.get_translator(1)
    result = translator.translate("UNKNOWN_KEY")
    assert result == "UNKNOWN_KEY"


def test_translation_parameters():
    """Test parameter substitution in translations"""

    # Create a simple translator for testing
    from app.telegram.i18n import Translator

    translator = Translator(
        "en",
        {
            "GREETING": "Hello ${name}, welcome to ${app}!",
            "COUNT": "You have ${count} messages.",
        },
    )

    # Test parameter substitution
    result = translator.translate("GREETING", name="John", app="Lexi")
    assert result == "Hello John, welcome to Lexi!"

    # Test with numbers
    result = translator.translate("COUNT", count=5)
    assert result == "You have 5 messages."

    # Test missing parameters (should use safe_substitute)
    result = translator.translate("GREETING", name="John")
    assert result == "Hello John, welcome to ${app}!"


if __name__ == "__main__":
    # Run tests manually if needed
    asyncio.run(test_user_language_detection(I18nService(MockUserCache({}))))
    print("All tests passed!")
