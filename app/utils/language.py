"""
Language utilities for Lexi bot
"""

from typing import Optional, Tuple

from thefuzz import fuzz


def get_user_language_message(language_code: str) -> str:
    """
    Get the language selection message in the user's language

    Args:
        language_code: The user's language code (e.g., 'en', 'ru', 'es')

    Returns:
        Message asking user to select a language to learn
    """
    messages = {
        "en": "What language would you like to learn?",
        "ru": "Какой язык вы хотите изучать?",
        "es": "¿Qué idioma te gustaría aprender?",
        "it": "Che lingua vorresti imparare?",
        "fr": "Quelle langue voulez-vous apprendre?",
        "be": "Якую мову вы хочаце вывучаць?",
        "uk": "Яку мову ви хочете вивчати?",
    }

    return messages.get(language_code, messages["en"])


def find_best_language_match(
    user_input: str, supported_languages: dict[str, str]
) -> Tuple[Optional[str], float]:
    """
    Find the best matching language from user input using fuzzy matching

    Args:
        user_input: User's language input
        supported_languages: Dictionary of language codes to display names

    Returns:
        Tuple of (language_code, confidence_score) or (None, 0.0) if no match
    """
    if not user_input:
        return None, 0.0

    user_input_lower = user_input.lower().strip()
    best_match = None
    best_score = 0.0

    # Check for exact matches first
    for code, name in supported_languages.items():
        if user_input_lower == code.lower() or user_input_lower == name.lower():
            return code, 100.0

    # Check for partial matches and fuzzy matching
    for code, name in supported_languages.items():
        # Check against language code
        code_score = fuzz.ratio(user_input_lower, code.lower())

        # Check against language name
        name_score = fuzz.ratio(user_input_lower, name.lower())

        # Check for partial matches
        partial_code_score = fuzz.partial_ratio(user_input_lower, code.lower())
        partial_name_score = fuzz.partial_ratio(user_input_lower, name.lower())

        # Take the best score for this language
        current_score = max(code_score, name_score, partial_code_score, partial_name_score)

        if current_score > best_score:
            best_score = current_score
            best_match = code

    # Only return a match if confidence is above threshold
    if best_score >= 70:
        return best_match, best_score

    return None, 0.0
