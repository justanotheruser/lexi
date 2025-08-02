#!/usr/bin/env python3
"""Simple test runner for i18n system"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.features.users.models import User
from app.telegram.i18n import I18nService, SyncI18nManager


class MockUserCache:
    def __init__(self, users: dict[int, User]):
        self.users = users

    async def get(self, user_id: int) -> User | None:
        return self.users.get(user_id)


async def run_basic_tests():
    """Run basic i18n tests"""

    print("🧪 Running i18n system tests...")
    print("=" * 50)

    # Create mock users
    users = {
        1: User(id=1, ui_language_code="en"),
        2: User(id=2, ui_language_code="ru"),
        3: User(id=3, ui_language_code="es"),
        4: User(id=4, ui_language_code="fr"),
        5: User(id=5, ui_language_code="de"),
    }

    # Create i18n service
    mock_cache = MockUserCache(users)
    i18n_service = I18nService(mock_cache)

    # Test 1: Basic translation
    print("✅ Test 1: Basic translation")
    translator = await i18n_service.get_translator(1)
    welcome = translator.translate("WELCOME")
    assert welcome == "👋 Welcome! I'll help you learn languages."
    print(f"   English: {welcome}")

    translator = await i18n_service.get_translator(2)
    welcome = translator.translate("WELCOME")
    assert welcome == "👋 Добро пожаловать! Я помогу вам изучать языки."
    print(f"   Russian: {welcome}")

    # Test 2: Parameter substitution
    print("\n✅ Test 2: Parameter substitution")
    translator = await i18n_service.get_translator(1)
    learn_msg = translator.translate("LETS_LEARN", language_name="Python")
    assert learn_msg == "✅ Ok, let's learn <b>Python</b>!"
    print(f"   English: {learn_msg}")

    translator = await i18n_service.get_translator(2)
    learn_msg = translator.translate("LETS_LEARN", language_name="Python")
    assert learn_msg == "✅ Хорошо, давайте изучать <b>Python</b>!"
    print(f"   Russian: {learn_msg}")

    # Test 3: Synchronous interface
    print("\n✅ Test 3: Synchronous interface")
    translator = await i18n_service.get_translator(1)
    sync_i18n = SyncI18nManager(i18n_service, 1, translator)

    welcome = sync_i18n["WELCOME"].translate()
    assert welcome == "👋 Welcome! I'll help you learn languages."
    print(f"   Sync English: {welcome}")

    learn_msg = sync_i18n["LETS_LEARN"].translate(language_name="JavaScript")
    assert learn_msg == "✅ Ok, let's learn <b>JavaScript</b>!"
    print(f"   Sync English with params: {learn_msg}")

    # Test 4: All languages
    print("\n✅ Test 4: All supported languages")
    test_cases = [
        (1, "en", "👋 Welcome! I'll help you learn languages."),
        (2, "ru", "👋 Добро пожаловать! Я помогу вам изучать языки."),
        (3, "es", "👋 ¡Bienvenido! Te ayudaré a aprender idiomas."),
        (4, "fr", "👋 Bienvenue! Je vous aiderai à apprendre les langues."),
        (5, "de", "👋 Willkommen! Ich helfe Ihnen beim Sprachenlernen."),
    ]

    for user_id, lang, expected in test_cases:
        translator = await i18n_service.get_translator(user_id)
        sync_i18n = SyncI18nManager(i18n_service, user_id, translator)
        welcome = sync_i18n["WELCOME"].translate()
        assert welcome == expected
        print(f"   {lang.upper()}: {welcome}")

    # Test 5: Default language fallback
    print("\n✅ Test 5: Default language fallback")
    translator = await i18n_service.get_translator(999)  # Non-existent user
    sync_i18n = SyncI18nManager(i18n_service, 999, translator)
    welcome = sync_i18n["WELCOME"].translate()
    assert welcome == "👋 Welcome! I'll help you learn languages."
    print(f"   Default (user 999): {welcome}")

    # Test 6: Unknown keys
    print("\n✅ Test 6: Unknown translation keys")
    translator = await i18n_service.get_translator(1)
    result = translator.translate("UNKNOWN_KEY")
    assert result == "UNKNOWN_KEY"
    print(f"   Unknown key: {result}")

    print("\n🎉 All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_basic_tests())
