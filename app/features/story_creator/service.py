from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select
from thefuzz import fuzz

from app.features.story_creator.models import Language


class StoryCreatorService:
    def __init__(self) -> None:
        self.supported_languages: dict[str, str] = {}
        self.supported_languages_in_user_language: dict[str, dict[str, str]] = {}

    async def start(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        async with sessionmaker() as session:
            self.supported_languages, self.supported_languages_in_user_language = (
                await load_languages_for_language_selection(session)
            )

    def find_best_language_match(
        self, user_input: str, user_ui_language: str
    ) -> tuple[str | None, float]:
        return find_best_language_match(
            user_input,
            self.supported_languages,
            user_ui_language,
            self.supported_languages_in_user_language,
        )

    def get_language_name_in_user_language(
        self,
        target_language_code: str,
        user_language: str,
    ) -> str:
        """
        Get the name of a language in the user's UI language

        Args:
            target_language_code: The language code to get the name for
            user_language: The user's UI language code
        Returns:
            The name of the target language in the user's UI language
        """
        if user_language in self.supported_languages_in_user_language:
            return self.supported_languages_in_user_language[user_language].get(
                target_language_code, target_language_code
            )
        return target_language_code


async def load_languages_for_language_selection(
    session: AsyncSession,
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """Load language data from database and return as dictionaries"""
    # Get all language records
    result = await session.execute(select(Language))
    language_records = result.scalars().all()

    supported_languages = {}
    supported_languages_in_user_language = {}

    for record in language_records:
        # For supported_languages, we want where language_code == user_language_code
        if record.language_code == record.user_language_code:
            supported_languages[record.language_code] = record.word

        # For supported_languages_in_user_language, group by user_language_code
        if record.user_language_code not in supported_languages_in_user_language:
            supported_languages_in_user_language[record.user_language_code] = {}
        supported_languages_in_user_language[record.user_language_code][
            record.language_code
        ] = record.word

    return supported_languages, supported_languages_in_user_language


def find_best_language_match(
    user_input: str,
    supported_languages: dict[str, str],
    user_language: str = "en",
    supported_languages_in_user_language: dict[str, dict[str, str]] | None = None,
) -> tuple[str | None, float]:
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
