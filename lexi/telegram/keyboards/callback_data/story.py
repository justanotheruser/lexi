from aiogram.filters.callback_data import CallbackData


class CDStoryChoice(CallbackData, prefix="story_choice"):
    choice_id: str


class CDVocabularyWord(CallbackData, prefix="vocab_word"):
    word: str


class CDStoryEnd(CallbackData, prefix="story_end"):
    pass
