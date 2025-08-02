"""
Database models for 'story creator' domain
"""

from sqlmodel import Field, PrimaryKeyConstraint, SQLModel


class Language(SQLModel, table=True):
    """Names of languages in different languages"""

    __table_args__ = (PrimaryKeyConstraint("language_code", "user_language_code"),)

    language_code: str = Field(max_length=10, foreign_key="supported_story_language.language_code")
    user_language_code: str = Field(
        max_length=10, foreign_key="supported_user_language.language_code"
    )
    word: str = Field(max_length=40)
