from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from .callback_data.menu import CDCreateStory, CDLanguageSelect, CDShowLanguages


def main_menu_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.button(text=i18n.buttons.create_story(), callback_data=CDCreateStory())
    return builder.as_markup()


def language_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.button(text=i18n.buttons.show_languages(), callback_data=CDShowLanguages())
    return builder.as_markup()


def language_selection_keyboard(locales: list[str], i18n: I18nContext) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # Add language buttons in a grid layout
    for lang_code in locales:
        if hasattr(i18n.messages, lang_code):
            lang_name = getattr(i18n.messages, lang_code)()
        else:
            lang_name = lang_code.upper()
        builder.button(text=lang_name, callback_data=CDLanguageSelect(language_code=lang_code))

    # Arrange buttons in a 3-column grid
    builder.adjust(3)
    return builder.as_markup()
