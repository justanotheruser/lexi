from aiogram.filters.callback_data import CallbackData


class CDCreateStory(CallbackData, prefix="create_story"):
    pass


class CDMenu(CallbackData, prefix="menu"):
    pass


class CDShowLanguages(CallbackData, prefix="show_languages"):
    pass


class CDLanguageSelect(CallbackData, prefix="lang_select"):
    language_code: str
