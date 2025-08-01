#!/usr/bin/env python3
"""
Simple test script for language selection functionality
"""

from app.settings import get_settings
from app.utils.language import find_best_language_match, get_user_language_message


def test_language_selection():
    """Test the language selection functionality"""
    cfg = get_settings()

    print("=== Testing Language Selection ===")

    # Test supported languages
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
        result, confidence = find_best_language_match(user_input, cfg.language.supported_languages)
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

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_language_selection()
