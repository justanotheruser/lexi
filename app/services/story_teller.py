from __future__ import annotations

import logging
import random
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, List, Optional, Tuple

from openai import AsyncOpenAI

from app.models.dto.story import (
    StoryBit,
    StoryChoice,
    StoryLogic,
    StoryParams,
    StorySession,
    VocabularyWord,
)
from app.models.dto.story_creation_params import StoryCreationParams
from app.prompts import (
    get_character_development_prompt,
    get_continue_story_prompt,
    get_initial_story_prompt,
    get_story_conclusion_prompt,
    get_vocabulary_definition_prompt,
)
from app.services.base import BaseService
from app.services.redis.repository import RedisRepository
from app.utils.key_builder import StorageKey

if TYPE_CHECKING:
    from app.config import AppConfig

logger: Final = logging.getLogger(__name__)


class StorySessionKey(StorageKey, prefix="story_session"):
    user_id: str


class VocabularyCacheKey(StorageKey, prefix="vocabulary"):
    word: str
    target_language: str
    native_language: str


class StoryTellerService(BaseService):
    """Service for story generation and management"""

    def __init__(self, config: AppConfig, redis_repo: RedisRepository) -> None:
        super().__init__()
        self.config = config
        self.redis_repo = redis_repo
        self.openai_client = AsyncOpenAI(
            api_key=config.story_teller.openai.api_key.get_secret_value()
        )

    def _get_story_session_key(self, user_id: int) -> StorageKey:
        """Get Redis key for story session"""
        return StorySessionKey(user_id=str(user_id))

    def _get_vocabulary_cache_key(
        self, word: str, target_language: str, native_language: str
    ) -> StorageKey:
        """Get Redis key for vocabulary cache"""
        return VocabularyCacheKey(
            word=word, target_language=target_language, native_language=native_language
        )

    async def create_story_session(
        self,
        user_id: int,
        params: StoryCreationParams,
    ) -> StorySession:
        """Create a new story session"""
        story_params = StoryParams(
            target_language_code=params.target_language_code,
            native_language_code=params.native_language_code,
            protagonist=params.protagonist,
            setting=params.setting,
            openai_model=self.config.story_teller.openai.model,
            max_tokens=self.config.story_teller.openai.max_tokens,
            temperature=self.config.story_teller.openai.temperature,
        )
        story_logic = StoryLogic(character_growths_moments_left=random.randint(1, 2))
        session = StorySession(
            user_id=user_id,
            params=story_params,
            logic=story_logic,
            created_at=datetime.now(UTC),
            last_updated=datetime.now(UTC),
        )

        key = self._get_story_session_key(user_id)
        await self.redis_repo.set(key, session)

        return session

    async def get_story_session(self, user_id: int) -> Optional[StorySession]:
        """Get existing story session"""
        key = self._get_story_session_key(user_id)
        return await self.redis_repo.get(key, StorySession)

    async def update_story_session(self, session: StorySession) -> None:
        """Update story session in Redis"""
        session.last_updated = datetime.utcnow()
        key = self._get_story_session_key(session.user_id)
        await self.redis_repo.set(key, session)

    async def delete_story_session(self, user_id: int) -> None:
        """Delete story session"""
        key = self._get_story_session_key(user_id)
        await self.redis_repo.delete(key)

    async def generate_initial_story(self, session: StorySession) -> StoryBit:
        """Generate the initial story bit"""
        prompt = get_initial_story_prompt(
            target_language=session.params.target_language_code,
            native_language=session.params.native_language_code,
            protagonist=session.params.protagonist,
            setting=session.params.setting,
        )

        response = await self.openai_client.chat.completions.create(
            model=session.params.openai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=session.params.max_tokens,
            temperature=session.params.temperature,
        )

        content = response.choices[0].message.content or ""
        story_text, choices = self._parse_story_response(content)
        key_words = self._extract_key_words(story_text)

        # Update session
        session.story_text = story_text
        session.choices = choices
        session.key_words = key_words
        session.turn_count = 1
        await self.update_story_session(session)

        return StoryBit(
            text=story_text,
            choices=[
                StoryChoice(text=choice, choice_id=str(i)) for i, choice in enumerate(choices, 1)
            ],
            key_words=key_words,
        )

    async def continue_story(self, session: StorySession, choice_text: str) -> StoryBit:
        """Continue the story based on user choice"""
        key_words = []
        content = ""

        if session.logic.character_growths_moments_left > 0 and random.random() < 0.25:
            prompt = get_character_development_prompt(
                target_language=session.params.target_language_code,
                native_language=session.params.native_language_code,
                protagonist=session.params.protagonist,
                story_so_far=session.story_text,
            )
            response = await self.openai_client.chat.completions.create(
                model=session.params.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=session.params.max_tokens,
                temperature=session.params.temperature,
            )
            content = response.choices[0].message.content or ""
            key_words = self._extract_key_words(content)
            session.logic.character_growths_moments_left -= 1
            await self.update_story_session(session)

        # Check if we should conclude the story
        should_conclude = session.turn_count >= 8  # After 8 turns, consider concluding

        if should_conclude:
            prompt = get_story_conclusion_prompt(
                target_language=session.params.target_language_code,
                native_language=session.params.native_language_code,
                protagonist=session.params.protagonist,
                setting=session.params.setting,
                story_so_far=session.story_text,
                user_choice=choice_text,
            )
        else:
            prompt = get_continue_story_prompt(
                target_language=session.params.target_language_code,
                native_language=session.params.native_language_code,
                protagonist=session.params.protagonist,
                setting=session.params.setting,
                story_so_far=session.story_text,
                user_choice=choice_text,
                turn_count=session.turn_count,
            )

        response = await self.openai_client.chat.completions.create(
            model=session.params.openai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=session.params.max_tokens,
            temperature=session.params.temperature,
        )

        content += response.choices[0].message.content or ""
        story_text, choices = self._parse_story_response(content)
        key_words = self._extract_key_words(story_text)

        # Update session
        session.story_text += "\n\n" + story_text
        session.choices = choices
        session.key_words.extend(key_words)
        session.turn_count += 1
        await self.update_story_session(session)

        return StoryBit(
            text=story_text,
            choices=[
                StoryChoice(text=choice, choice_id=str(i)) for i, choice in enumerate(choices, 1)
            ],
            key_words=key_words,
        )

    async def get_vocabulary_definition(
        self,
        word: str,
        target_language: str,
        native_language: str,
        context: str,
    ) -> VocabularyWord:
        """Get vocabulary definition and translation"""
        # Check cache first
        cache_key = self._get_vocabulary_cache_key(word, target_language, native_language)
        cached = await self.redis_repo.get(cache_key, VocabularyWord)
        if cached:
            return cached

        # Generate definition
        prompt = get_vocabulary_definition_prompt(word, target_language, native_language, context)

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3,
        )

        content = response.choices[0].message.content or ""
        definition, translation = self._parse_vocabulary_response(content)

        vocab_word = VocabularyWord(
            word=word,
            definition=definition,
            translation=translation,
            language_code=target_language,
        )

        # Cache the result
        await self.redis_repo.set(cache_key, vocab_word, ex=3600)  # Cache for 1 hour

        return vocab_word

    def _parse_story_response(self, content: str) -> Tuple[str, List[str]]:
        """Parse story response to extract text and choices"""
        lines = content.strip().split("\n")
        story_lines = []
        choices = []

        in_choices = False
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if we've reached the choices section
            if re.match(r"^\d+\.", line):
                in_choices = True
                choices.append(line.split(".", 1)[1].strip())
            elif in_choices:
                # Continue parsing choices
                choices.append(line)
            else:
                # Still in story text
                story_lines.append(line)

        story_text = "\n".join(story_lines)
        return story_text, choices

    def _parse_vocabulary_response(self, content: str) -> Tuple[str, str]:
        """Parse vocabulary response to extract definition and translation"""
        definition = ""
        translation = ""

        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("Definition:"):
                definition = line.split("Definition:", 1)[1].strip()
            elif line.startswith("Translation:"):
                translation = line.split("Translation:", 1)[1].strip()

        return definition, translation

    def _extract_key_words(self, text: str) -> List[str]:
        """Extract key words from story text (MVP: random words longer than threshold)"""
        # Simple MVP implementation: extract words longer than 5 characters
        words = re.findall(r"\b\w+\b", text.lower())
        long_words = [word for word in words if len(word) > 5 and word.isalpha()]

        # Return 1-2 random words (for MVP, just take first 2)
        return long_words[:2] if len(long_words) >= 2 else long_words[:1]

    def format_story_text_with_key_words(self, text: str, key_words: List[str]) -> str:
        """Format story text with bolded key words"""
        formatted_text = text
        for word in key_words:
            # Simple word replacement (case-insensitive)
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            formatted_text = pattern.sub(f"**{word}**", formatted_text)

        return formatted_text
