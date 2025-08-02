"""Module for internationalization of UI"""

from string import Template
from typing import Any, Literal, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.users.user_cache import UserCache
from app.models import PhraseTranslation
from app.settings import get_settings

Phrase = Literal[
    "WHAT_LANGUAGE_YOU_WANT_LEARN",
    "LETS_LEARN",
    "LANGUAGE_NOT_SUPPORTED",
    "WELCOME",
    "LANGUAGE_SELECTED",
    "DEFINE_PROTAGONIST",
    "DEFINE_SETTING",
    "CONTENT_INAPPROPRIATE",
    "STORY_PARAMETERS_READY",
]


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
        self._translators: dict[str, Translator] = {}

    async def load_translators_from_db(self, session: AsyncSession) -> None:
        """Load translators from database"""
        if self._translators:
            return  # Already loaded

        # Get all phrase translations from database
        result = await session.execute(select(PhraseTranslation))
        phrase_translations = result.scalars().all()

        # Group translations by language code
        translations_by_language: dict[str, dict[Phrase, str]] = {}

        for translation in phrase_translations:
            if translation.language_code not in translations_by_language:
                translations_by_language[translation.language_code] = {}

            # Cast the phrase_enum to Phrase type
            phrase_key = cast(Phrase, translation.phrase_enum)
            translations_by_language[translation.language_code][
                phrase_key
            ] = translation.translation

        # Create translators for each language
        for language_code, translations in translations_by_language.items():
            self._translators[language_code] = Translator(language_code, translations)

    async def get_user_language(self, user_id: int) -> str:
        """Get user's UI language from cache or return default"""
        user = await self.user_cache.get(user_id)
        if user and user.ui_language_code in self._translators:
            return user.ui_language_code
        return self.default_language_code

    async def get_i18n(self, user_id: int) -> I18nManager:
        """Get i18n manager for user's language"""
        language = await self.get_user_language(user_id)
        translator = self._translators.get(
            language, self._translators.get("en", Translator("en", {}))
        )
        return I18nManager(translator)
