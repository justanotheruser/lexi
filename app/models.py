"""
Database models for Lexi bot
"""

from sqlmodel import Field, PrimaryKeyConstraint, SQLModel


class SupportedUserLanguage(SQLModel, table=True):
    __tablename__ = "supported_user_language"  # type: ignore

    language_code: str = Field(primary_key=True, max_length=10)


class SupportedStoryLanguage(SQLModel, table=True):
    __tablename__ = "supported_story_language"  # type: ignore

    language_code: str = Field(primary_key=True, max_length=10)


class Language(SQLModel, table=True):
    """Names of languages in different languages"""

    __table_args__ = (PrimaryKeyConstraint("language_code", "user_language_code"),)

    language_code: str = Field(max_length=10)
    user_language_code: str = Field(max_length=10)
    word: str = Field(max_length=40)
