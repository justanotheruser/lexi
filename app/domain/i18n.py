"""Module for internationalization of UI"""

from string import Template


class Translator:
    def __init__(self, language: str, translations: dict[str, str]) -> None:
        self.language = language
        self.translations = translations

    def translate(self, key: str, **kwargs):
        text = self.translations.get(key, key)
        if len(kwargs) == 0:
            return text
        return Template(text).safe_substitute(**kwargs)


ru_translator = Translator(
    language="ru",
    translations={
        "WHAT_LANGUAGE_YOU_WANT_LEARN": "Какой язык вы хотите изучать?",
        "LETS_LEARN": "✅ Хорошо, давайте изучать <b>$1</b>!",
    },
)
en_translator = Translator(
    language="ru",
    translations={
        "WHAT_LANGUAGE_YOU_WANT_LEARN": "What language would you like to learn?",
        "LETS_LEARN": "✅ Ok, let's learn <b>$1</b>!",
    },
)
translator_store = {"ru": ru_translator, "en": en_translator}


# Для каждого языка из таблицы supported_user_languages:
# Загрузить все строки из ui_phrase_translation где language=язык
# Из строки создать словарь вида {phrase_enum: translation}
# Создать Translator для языка language, куда передать этот словарь
# Добавить Translator в translator_store
