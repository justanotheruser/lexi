"""
Database models for Lexi bot
"""

from sqlmodel import Field, SQLModel


class SupportedUserLanguage(SQLModel, table=True):
    __tablename__ = "supported_user_language"  # type: ignore

    language_code: str = Field(primary_key=True, max_length=10)


class SupportedStoryLanguage(SQLModel, table=True):
    __tablename__ = "supported_story_language"  # type: ignore

    language_code: str = Field(primary_key=True, max_length=10)
