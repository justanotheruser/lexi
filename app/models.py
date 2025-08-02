"""
Database models for Lexi bot
"""

from sqlmodel import Field, PrimaryKeyConstraint, SQLModel, Text


class SupportedUserLanguage(SQLModel, table=True):
    __tablename__ = "supported_user_language"  # type: ignore

    language_code: str = Field(primary_key=True, max_length=10)


class SupportedStoryLanguage(SQLModel, table=True):
    __tablename__ = "supported_story_language"  # type: ignore

    language_code: str = Field(primary_key=True, max_length=10)


class PhraseTranslation(SQLModel, table=True):
    __tablename__ = "phrase_translation"  # type: ignore
    __table_args__ = (PrimaryKeyConstraint("language_code", "phrase_enum"),)

    language_code: str = Field(max_length=10, foreign_key="supported_user_language.language_code")
    phrase_enum: str = Field(sa_type=Text)
    translation: str = Field(sa_type=Text)
