"""Module for internationalization of UI"""

from string import Template
from typing import Any, Literal

from app.features.users.user_cache import UserCache
from app.settings import get_settings

Phrase = Literal["WHAT_LANGUAGE_YOU_WANT_LEARN", "LETS_LEARN", "LANGUAGE_NOT_SUPPORTED", "WELCOME"]


class Translator:
    """Translator for a specific language"""

    def __init__(self, language: str, translations: dict[Phrase, str]) -> None:
        self.language = language
        self.translations = translations

    def translate(self, key: Phrase, **kwargs: Any) -> str:
        """Translate a key with optional parameters"""
        text = self.translations.get(key, key)
        if not kwargs:
            return text
        return Template(text).safe_substitute(**kwargs)


class TranslatableKey:
    """A translatable key that can be translated for a specific user"""

    def __init__(self, translator: Translator, key: Phrase) -> None:
        self._translator = translator
        self._key: Phrase = key

    def translate(self, **kwargs: Any) -> str:
        """Translate this key for a language of translator"""
        return self._translator.translate(self._key, **kwargs)


class I18nManager:
    """Provides dict-like interface for translating phrases"""

    def __init__(self, translator: Translator) -> None:
        self.language = translator.language
        self._translator = translator

    def __getitem__(self, key: Phrase) -> "TranslatableKey":
        """Get a translatable key that can be used with user_id"""
        return TranslatableKey(self._translator, key)


class I18nService:
    """Service for internationalization that handles user language detection"""

    def __init__(self, user_cache: UserCache) -> None:
        self.user_cache = user_cache
        self.default_language_code = get_settings().language.default_language_code
        self._translators = self._create_translators()

    def _create_translators(self) -> dict[str, Translator]:
        """Create translators for all supported languages"""
        return {
            "ru": Translator(
                language="ru",
                translations={
                    "WHAT_LANGUAGE_YOU_WANT_LEARN": "Какой язык вы хотите изучать?",
                    "LETS_LEARN": "✅ Хорошо, давайте изучать <b>${language_name}</b>!",
                    "LANGUAGE_NOT_SUPPORTED": "❌ Язык не поддерживается. Попробуйте снова с поддерживаемым языком.",
                    "WELCOME": "👋 Добро пожаловать! Я помогу вам изучать языки.",
                },
            ),
            "en": Translator(
                language="en",
                translations={
                    "WHAT_LANGUAGE_YOU_WANT_LEARN": "What language would you like to learn?",
                    "LETS_LEARN": "✅ Ok, let's learn <b>${language_name}</b>!",
                    "LANGUAGE_NOT_SUPPORTED": "❌ Language not supported. Please try again with a supported language.",
                    "WELCOME": "👋 Welcome! I'll help you learn languages.",
                },
            ),
            "es": Translator(
                language="es",
                translations={
                    "WHAT_LANGUAGE_YOU_WANT_LEARN": "¿Qué idioma te gustaría aprender?",
                    "LETS_LEARN": "✅ Ok, vamos a aprender <b>${language_name}</b>!",
                    "LANGUAGE_NOT_SUPPORTED": "❌ Idioma no soportado. Inténtalo de nuevo con un idioma soportado.",
                    "WELCOME": "👋 ¡Bienvenido! Te ayudaré a aprender idiomas.",
                },
            ),
            "fr": Translator(
                language="fr",
                translations={
                    "WHAT_LANGUAGE_YOU_WANT_LEARN": "Quelle langue voulez-vous apprendre?",
                    "LETS_LEARN": "✅ Ok, apprenons <b>${language_name}</b>!",
                    "LANGUAGE_NOT_SUPPORTED": "❌ Langue non prise en charge. Veuillez réessayer avec une langue prise en charge.",
                    "WELCOME": "👋 Bienvenue! Je vous aiderai à apprendre les langues.",
                },
            ),
            "de": Translator(
                language="de",
                translations={
                    "WHAT_LANGUAGE_YOU_WANT_LEARN": "Welche Sprache möchten Sie lernen?",
                    "LETS_LEARN": "✅ Ok, lass uns <b>${language_name}</b> lernen!",
                    "LANGUAGE_NOT_SUPPORTED": "❌ Sprache wird nicht unterstützt. Bitte versuchen Sie es erneut mit einer unterstützten Sprache.",
                    "WELCOME": "👋 Willkommen! Ich helfe Ihnen beim Sprachenlernen.",
                },
            ),
        }

    async def get_user_language(self, user_id: int) -> str:
        """Get user's UI language from cache or return default"""
        user = await self.user_cache.get(user_id)
        if user and user.ui_language_code in self._translators:
            return user.ui_language_code
        return self.default_language_code

    async def get_i18n(self, user_id: int) -> I18nManager:
        """Get i18n manager for user's language"""
        language = await self.get_user_language(user_id)
        translator = self._translators.get(language, self._translators["en"])
        return I18nManager(translator)
