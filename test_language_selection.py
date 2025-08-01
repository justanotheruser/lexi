#!/usr/bin/env python3
"""
Simple test script for language selection functionality
"""

from app.settings import get_settings
from app.utils.language import (
    find_best_language_match,
    get_language_confirmation_message,
    get_language_not_supported_message,
    get_user_language_message,
)


def test_language_selection():
    """Test the language selection functionality"""
    cfg = get_settings()

    print("=== Testing Language Selection (English) ===")

    # Test supported languages in English
    test_cases = [
        ("english", "en"),
        ("russian", "ru"),
        ("spanish", "es"),
        ("italian", "it"),
        ("french", "fr"),
        ("беларусский", "be"),
        ("украинский", "uk"),
        ("eng", "en"),
        ("rus", "ru"),
        ("spa", "es"),
        ("invalid", None),
    ]

    for user_input, expected_code in test_cases:
        result, confidence = find_best_language_match(
            user_input,
            cfg.language.supported_languages,
            "en",
            cfg.language.supported_languages_in_user_language,
        )
        status = "✅ PASS" if result == expected_code else "❌ FAIL"
        print(
            f"{status} Input: '{user_input}' -> Expected: {expected_code}, Got: {result}, Confidence: {confidence}"
        )

    print("\n=== Testing Language Selection (Russian) ===")

    # Test supported languages in Russian
    test_cases_russian = [
        ("французский", "fr"),
        ("английский", "en"),
        ("испанский", "es"),
        ("итальянский", "it"),
        ("русский", "ru"),
        ("беларусский", "be"),
        ("украинский", "uk"),
        ("франц", "fr"),
        ("англ", "en"),
        ("исп", "es"),
        ("invalid", None),
    ]

    for user_input, expected_code in test_cases_russian:
        result, confidence = find_best_language_match(
            user_input,
            cfg.language.supported_languages,
            "ru",
            cfg.language.supported_languages_in_user_language,
        )
        status = "✅ PASS" if result == expected_code else "❌ FAIL"
        print(
            f"{status} Input: '{user_input}' -> Expected: {expected_code}, Got: {result}, Confidence: {confidence}"
        )

    print("\n=== Testing Language Messages ===")

    # Test language messages
    test_languages = ["en", "ru", "es", "it", "fr", "be", "uk"]
    for lang in test_languages:
        message = get_user_language_message(lang)
        print(f"{lang}: {message}")

    print("\n=== Testing Confirmation Messages ===")

    # Test confirmation messages
    for lang in test_languages:
        message = get_language_confirmation_message(lang)
        print(f"{lang}: {message}")

    print("\n=== Testing Error Messages ===")

    # Test error messages
    for lang in test_languages:
        message = get_language_not_supported_message(lang)
        print(f"{lang}: {message}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_language_selection()
