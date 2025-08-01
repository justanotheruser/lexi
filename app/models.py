"""
Database models for Lexi bot
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model representing Telegram users"""

    id: int = Field(primary_key=True)  # Telegram User ID
    native_language_code: str = Field(max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Story(SQLModel, table=True):
    """Story model representing completed stories"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    target_language_code: str = Field(max_length=10)
    protagonist: str
    setting: str
    full_story_text: Optional[str] = None
    cover_image_url: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None


class UserVocabularyProgress(SQLModel, table=True):
    """Vocabulary progress tracking for users"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    word: str
    language_code: str = Field(max_length=10)
    times_seen: int = Field(default=0)
    times_quized: Optional[int] = None
    correct_answers: Optional[int] = None
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
