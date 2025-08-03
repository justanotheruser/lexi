"""Story generation prompts for Lexi bot"""

from typing import List


def get_initial_story_prompt(
    target_language: str,
    native_language: str,
    protagonist: str,
    setting: str,
    tone_adjective_1: str = "fun",
    tone_adjective_2: str = "encouraging",
) -> str:
    """Generate initial story prompt"""
    return f"""You are Lexi, a fun and encouraging AI storyteller for a child learning {target_language}.
Their native language is {native_language}.
The story is about a {protagonist} in a {setting}.
The tone should be {tone_adjective_1}, {tone_adjective_2}, and suitable for a 10-year-old.
Write the first paragraph of the story in {target_language}.
Keep the story text under 75 words.
After the story text, on a new line, provide two choices for the user to continue the story, formatted as a numbered list. Example:
1. Choice one...
2. Choice two..."""


def get_continue_story_prompt(
    target_language: str,
    native_language: str,
    protagonist: str,
    setting: str,
    story_so_far: str,
    user_choice: str,
    turn_count: int,
) -> str:
    """Generate story continuation prompt"""
    return f"""You are Lexi, a fun and encouraging AI storyteller for a child learning {target_language}.
Their native language is {native_language}.
The story is about a {protagonist} in a {setting}.

Story so far:
{story_so_far}

The user chose: {user_choice}

Continue the story based on this choice. Write 1-2 paragraphs in {target_language}.
Keep the story text under 150 words total.
After the story text, on a new line, provide two choices for the user to continue the story, formatted as a numbered list.

If this is turn {turn_count} or higher, consider concluding the story naturally in the next 1-2 paragraphs."""


def get_vocabulary_definition_prompt(
    word: str,
    target_language: str,
    native_language: str,
    context: str,
) -> str:
    """Generate vocabulary definition prompt"""
    return f"""You are a helpful language teacher. Provide a simple definition and translation for the word "{word}" from this context:

Context: {context}

Target language: {target_language}
Native language: {native_language}

Provide your response in this exact format:
Definition: [simple definition in {target_language}]
Translation: [translation in {native_language}]

Keep both definition and translation simple and suitable for a 10-year-old child."""


def get_story_conclusion_prompt(
    target_language: str,
    native_language: str,
    protagonist: str,
    setting: str,
    story_so_far: str,
    user_choice: str,
) -> str:
    """Generate story conclusion prompt"""
    return f"""You are Lexi, a fun and encouraging AI storyteller for a child learning {target_language}.
Their native language is {native_language}.
The story is about a {protagonist} in a {setting}.

Story so far:
{story_so_far}

The user chose: {user_choice}

Please conclude the story in a satisfying way in the next 1-2 paragraphs in {target_language}.
Keep the conclusion under 100 words.
Make it a happy, satisfying ending suitable for a 10-year-old child."""
