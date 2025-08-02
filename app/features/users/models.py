"""
Database models for 'users' domain
"""

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    # Telegram id of user
    id: int = Field(primary_key=True)
    ui_language_code: str = Field(
        max_length=10, foreign_key="supported_user_language.language_code"
    )
    last_story_language_code: str | None = Field(
        max_length=10,
        nullable=True,
        foreign_key="supported_story_language.language_code",
        default=None,
    )
    use_last_story_language: bool = Field(default=True)
