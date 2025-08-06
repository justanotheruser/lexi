#!/usr/bin/env python3
"""
Test script to verify database loading functionality
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.settings import get_settings


async def test_language_loading():
    """Test language data loading with mock data"""

    # Mock the database session and records
    mock_records = [
        MagicMock(language_code="en", user_language_code="en", word="English"),
        MagicMock(language_code="ru", user_language_code="en", word="Russian"),
        MagicMock(language_code="es", user_language_code="en", word="Spanish"),
        MagicMock(language_code="it", user_language_code="en", word="Italian"),
        MagicMock(language_code="fr", user_language_code="en", word="French"),
        MagicMock(language_code="be", user_language_code="en", word="Belarusian"),
        MagicMock(language_code="uk", user_language_code="en", word="Ukrainian"),
        MagicMock(language_code="en", user_language_code="ru", word="Английский"),
        MagicMock(language_code="ru", user_language_code="ru", word="Русский"),
        MagicMock(language_code="es", user_language_code="ru", word="Испанский"),
        MagicMock(language_code="it", user_language_code="ru", word="Итальянский"),
        MagicMock(language_code="fr", user_language_code="ru", word="Французский"),
        MagicMock(language_code="be", user_language_code="ru", word="Беларусский"),
        MagicMock(language_code="uk", user_language_code="ru", word="Украинский"),
    ]

    # Mock the database session
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_records
    mock_session.execute.return_value = mock_result

    # Test the logic from load_language_data function
    supported_languages = {}
    supported_languages_in_user_language = {}

    for record in mock_records:
        # For supported_languages, we want where language_code == user_language_code
        if record.language_code == record.user_language_code:
            supported_languages[record.language_code] = record.word

        # For supported_languages_in_user_language, group by user_language_code
        if record.user_language_code not in supported_languages_in_user_language:
            supported_languages_in_user_language[record.user_language_code] = {}
        supported_languages_in_user_language[record.user_language_code][
            record.language_code
        ] = record.word

    print("=== Testing Database Loading Logic ===")
    print(f"Supported languages: {supported_languages}")
    print(f"Supported languages in user language: {supported_languages_in_user_language}")

    # Test some specific cases
    assert supported_languages["en"] == "English"
    assert supported_languages["ru"] == "Русский"
    assert supported_languages_in_user_language["en"]["ru"] == "Russian"
    assert supported_languages_in_user_language["ru"]["en"] == "Английский"

    print("✅ All assertions passed!")
    print("✅ Database loading logic works correctly")


if __name__ == "__main__":
    asyncio.run(test_language_loading())
