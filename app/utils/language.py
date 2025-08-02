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


def get_language_confirmation_message(language_code: str) -> str:
    """
    Get the language confirmation message in the user's language

    Args:
        language_code: The user's language code (e.g., 'en', 'ru', 'es')

    Returns:
        Message confirming language selection
    """
    messages = {
        "en": "Ok, let's learn",
        "ru": "Хорошо, давайте изучать",
        "es": "Ok, vamos a aprender",
        "it": "Ok, impariamo",
        "fr": "Ok, apprenons",
        "be": "Добра, давайце вывучаць",
        "uk": "Добре, давайте вивчати",
    }

    return messages.get(language_code, messages["en"])


def get_language_not_supported_message(language_code: str) -> str:
    """
    Get the language not supported message in the user's language

    Args:
        language_code: The user's language code (e.g., 'en', 'ru', 'es')

    Returns:
        Message indicating language is not supported
    """
    messages = {
        "en": "Language not supported. Please try again with a supported language.",
        "ru": "Язык не поддерживается. Попробуйте снова с поддерживаемым языком.",
        "es": "Idioma no soportado. Inténtalo de nuevo con un idioma soportado.",
        "it": "Lingua non supportata. Riprova con una lingua supportata.",
        "fr": "Langue non prise en charge. Veuillez réessayer avec une langue prise en charge.",
        "be": "Мова не падтрымліваецца. Паспрабуйце зноў з падтрымліваемай мовай.",
        "uk": "Мова не підтримується. Спробуйте ще раз з підтримуваною мовою.",
    }

    return messages.get(language_code, messages["en"])


def get_language_name_in_user_language(
    target_language_code: str,
    user_language: str,
    supported_languages_in_user_language: dict[str, dict[str, str]],
) -> str:
    """
    Get the name of a language in the user's UI language

    Args:
        target_language_code: The language code to get the name for
        user_language: The user's UI language code
        supported_languages_in_user_language: Dictionary of language names in different languages

    Returns:
        The name of the target language in the user's UI language
    """
    if user_language in supported_languages_in_user_language:
        return supported_languages_in_user_language[user_language].get(
            target_language_code, target_language_code
        )
    return target_language_code


def get_learning_phrase_in_target_language(target_language_code: str) -> str:
    """
    Get the learning phrase in the target language

    Args:
        target_language_code: The language code to get the phrase in

    Returns:
        The learning phrase in the target language
    """
    phrases = {
        "en": "Let's learn English",
        "ru": "Давайте учить русский",
        "es": "Vamos a aprender español",
        "it": "Impariamo l'italiano",
        "fr": "Apprenons le français",
        "be": "Давайце вывучаць беларускую мову",
        "uk": "Давайте вивчати українську мову",
    }

    return phrases.get(target_language_code, f"Let's learn {target_language_code}")


def find_best_language_match(
    user_input: str,
    supported_languages: dict[str, str],
    user_language: str = "en",
    supported_languages_in_user_language: Optional[dict[str, dict[str, str]]] = None,
) -> Tuple[Optional[str], float]:
    """
    Find the best matching language from user input using fuzzy matching

    Args:
        user_input: User's language input
        supported_languages: Dictionary of language codes to display names
        user_language: User's UI language code
        supported_languages_in_user_language: Dictionary of language names in different languages

    Returns:
        Tuple of (language_code, confidence_score) or (None, 0.0) if no match
    """
    if not user_input:
        return None, 0.0

    user_input_lower = user_input.lower().strip()
    best_match = None
    best_score = 0.0

    # Get language names in user's UI language
    user_language_names = {}
    if (
        supported_languages_in_user_language
        and user_language in supported_languages_in_user_language
    ):
        user_language_names = supported_languages_in_user_language[user_language]

    # Check for exact matches first (both in English and user's language)
    for code, name in supported_languages.items():
        if user_input_lower == code.lower() or user_input_lower == name.lower():
            return code, 100.0

    # Check exact matches in user's language
    for code, name in user_language_names.items():
        if user_input_lower == name.lower():
            return code, 100.0

    # Check for partial matches and fuzzy matching
    for code, name in supported_languages.items():
        # Check against language code
        code_score = fuzz.ratio(user_input_lower, code.lower())

        # Check against language name in English
        name_score = fuzz.ratio(user_input_lower, name.lower())

        # Check for partial matches
        partial_code_score = fuzz.partial_ratio(user_input_lower, code.lower())
        partial_name_score = fuzz.partial_ratio(user_input_lower, name.lower())

        # Take the best score for this language
        current_score = max(code_score, name_score, partial_code_score, partial_name_score)

        if current_score > best_score:
            best_score = current_score
            best_match = code

    # Also check against language names in user's UI language
    for code, name in user_language_names.items():
        # Check against language name in user's language
        name_score = fuzz.ratio(user_input_lower, name.lower())

        # Check for partial matches
        partial_name_score = fuzz.partial_ratio(user_input_lower, name.lower())

        # Take the best score for this language
        current_score = max(name_score, partial_name_score)

        if current_score > best_score:
            best_score = current_score
            best_match = code

    # Only return a match if confidence is above threshold
    if best_score >= 70:
        return best_match, best_score

    return None, 0.0
