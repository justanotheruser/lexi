from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class StoryParams(BaseModel):
    """Story parameters for story creation"""

    target_language_code: str
    protagonist: str
    setting: str
    native_language_code: str


class StorySession(BaseModel):
    """Story session data stored in Redis"""

    user_id: int
    params: StoryParams
    story_text: str = ""
    choices: List[str] = []
    key_words: List[str] = []
    turn_count: int = 0
    created_at: datetime
    last_updated: datetime


class VocabularyWord(BaseModel):
    """Vocabulary word with translation and definition"""

    word: str
    definition: str
    translation: str
    language_code: str


class StoryChoice(BaseModel):
    """Story choice for user selection"""

    text: str
    choice_id: str


class StoryBit(BaseModel):
    """A single story bit with text and choices"""

    text: str
    choices: List[StoryChoice]
    key_words: List[str]
