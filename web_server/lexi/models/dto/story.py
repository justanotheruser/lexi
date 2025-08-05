import random
from datetime import datetime

from pydantic import BaseModel


class StoryParams(BaseModel):
    """Complete story parameters for story creation"""

    target_language_code: str
    protagonist: str
    setting: str
    native_language_code: str
    openai_model: str
    max_tokens: int
    temperature: float


class StoryLogic(BaseModel):
    character_growths_moments_left: int


class StorySession(BaseModel):
    """Story session data stored in Redis"""

    user_id: int
    params: StoryParams
    logic: StoryLogic
    story_text: str = ""
    choices: list[str] = []
    key_words: list[str] = []
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
    choices: list[StoryChoice]
    key_words: list[str]
