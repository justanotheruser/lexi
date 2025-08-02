"""Populate phrase translations

Revision ID: populate_phrase_translations
Revises: 7061ba58db1e
Create Date: 2025-08-02 15:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel

# pylint: disable=all
from alembic import op

# revision identifiers, used by Alembic.
revision = "populate_phrase_translations"
down_revision = "7061ba58db1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert phrase translations for all supported languages
    phrase_translations = [
        # Russian translations
        ("ru", "WHAT_LANGUAGE_YOU_WANT_LEARN", "Какой язык вы хотите изучать?"),
        ("ru", "LETS_LEARN", "✅ Хорошо, давайте изучать <b>${language_name}</b>!"),
        (
            "ru",
            "LANGUAGE_NOT_SUPPORTED",
            "❌ Язык не поддерживается. Попробуйте снова с поддерживаемым языком.",
        ),
        ("ru", "WELCOME", "👋 Добро пожаловать! Я помогу вам изучать языки."),
        ("ru", "LANGUAGE_SELECTED", "✅ Отлично! Вы выбрали <b>${language_name}</b>."),
        (
            "ru",
            "DEFINE_PROTAGONIST",
            "Теперь опишите главного героя вашей истории. Например: ''храбрый рыцарь'', ''умная лиса'', ''маленький робот''.",
        ),
        (
            "ru",
            "DEFINE_SETTING",
            "Отлично! Теперь опишите место действия. Например: ''волшебный лес'', ''космическая станция'', ''подводный город''.",
        ),
        (
            "ru",
            "CONTENT_INAPPROPRIATE",
            "❌ Это описание не подходит для детской истории. Попробуйте что-то более подходящее для детей.",
        ),
        ("ru", "STORY_PARAMETERS_READY", "🎉 Отлично! Ваши параметры истории готовы:"),
        # English translations
        ("en", "WHAT_LANGUAGE_YOU_WANT_LEARN", "What language would you like to learn?"),
        ("en", "LETS_LEARN", "✅ Ok, let''s learn <b>${language_name}</b>!"),
        (
            "en",
            "LANGUAGE_NOT_SUPPORTED",
            "❌ Language not supported. Please try again with a supported language.",
        ),
        ("en", "WELCOME", "👋 Welcome! I'll help you learn languages."),
        ("en", "LANGUAGE_SELECTED", "✅ Great! You selected <b>${language_name}</b>."),
        (
            "en",
            "DEFINE_PROTAGONIST",
            "Now describe the main character of your story. For example: 'brave knight', 'clever fox', 'little robot'.",
        ),
        (
            "en",
            "DEFINE_SETTING",
            "Great! Now describe the setting. For example: 'magical forest', 'space station', 'underwater city'.",
        ),
        (
            "en",
            "CONTENT_INAPPROPRIATE",
            "❌ This description is not suitable for a children's story. Please try something more appropriate for kids.",
        ),
        ("en", "STORY_PARAMETERS_READY", "🎉 Perfect! Your story parameters are ready:"),
        # Spanish translations
        ("es", "WHAT_LANGUAGE_YOU_WANT_LEARN", "¿Qué idioma te gustaría aprender?"),
        ("es", "LETS_LEARN", "✅ Ok, vamos a aprender <b>${language_name}</b>!"),
        (
            "es",
            "LANGUAGE_NOT_SUPPORTED",
            "❌ Idioma no soportado. Inténtalo de nuevo con un idioma soportado.",
        ),
        ("es", "WELCOME", "👋 ¡Bienvenido! Te ayudaré a aprender idiomas."),
        ("es", "LANGUAGE_SELECTED", "✅ ¡Genial! Seleccionaste <b>${language_name}</b>."),
        (
            "es",
            "DEFINE_PROTAGONIST",
            "Ahora describe el personaje principal de tu historia. Por ejemplo: 'valiente caballero', 'zorro astuto', 'pequeño robot'.",
        ),
        (
            "es",
            "DEFINE_SETTING",
            "¡Genial! Ahora describe el escenario. Por ejemplo: 'bosque mágico', 'estación espacial', 'ciudad submarina'.",
        ),
        (
            "es",
            "CONTENT_INAPPROPRIATE",
            "❌ Esta descripción no es adecuada para una historia infantil. Intenta algo más apropiado para niños.",
        ),
        (
            "es",
            "STORY_PARAMETERS_READY",
            "🎉 ¡Perfecto! Los parámetros de tu historia están listos:",
        ),
        # French translations
        ("fr", "WHAT_LANGUAGE_YOU_WANT_LEARN", "Quelle langue voulez-vous apprendre?"),
        ("fr", "LETS_LEARN", "✅ Ok, apprenons <b>${language_name}</b>!"),
        (
            "fr",
            "LANGUAGE_NOT_SUPPORTED",
            "❌ Langue non prise en charge. Veuillez réessayer avec une langue prise en charge.",
        ),
        ("fr", "WELCOME", "👋 Bienvenue! Je vous aiderai à apprendre les langues."),
        ("fr", "LANGUAGE_SELECTED", "✅ Super! Vous avez sélectionné <b>${language_name}</b>."),
        (
            "fr",
            "DEFINE_PROTAGONIST",
            "Maintenant, décrivez le personnage principal de votre histoire. Par exemple: 'brave chevalier', 'renard rusé', 'petit robot'.",
        ),
        (
            "fr",
            "DEFINE_SETTING",
            "Super! Maintenant, décrivez le décor. Par exemple: 'forêt magique', 'station spatiale', 'ville sous-marine'.",
        ),
        (
            "fr",
            "CONTENT_INAPPROPRIATE",
            "❌ Cette description n'est pas appropriée pour une histoire d'enfants. Essayez quelque chose de plus approprié pour les enfants.",
        ),
        (
            "fr",
            "STORY_PARAMETERS_READY",
            "🎉 Parfait! Les paramètres de votre histoire sont prêts:",
        ),
        # German translations
        ("de", "WHAT_LANGUAGE_YOU_WANT_LEARN", "Welche Sprache möchten Sie lernen?"),
        ("de", "LETS_LEARN", "✅ Ok, lass uns <b>${language_name}</b> lernen!"),
        (
            "de",
            "LANGUAGE_NOT_SUPPORTED",
            "❌ Sprache wird nicht unterstützt. Bitte versuchen Sie es erneut mit einer unterstützten Sprache.",
        ),
        ("de", "WELCOME", "👋 Willkommen! Ich helfe Ihnen beim Sprachenlernen."),
        ("de", "LANGUAGE_SELECTED", "✅ Toll! Sie haben <b>${language_name}</b> ausgewählt."),
        (
            "de",
            "DEFINE_PROTAGONIST",
            "Beschreiben Sie jetzt den Hauptcharakter Ihrer Geschichte. Zum Beispiel: 'tapferer Ritter', 'schlauer Fuchs', 'kleiner Roboter'.",
        ),
        (
            "de",
            "DEFINE_SETTING",
            "Toll! Beschreiben Sie jetzt die Umgebung. Zum Beispiel: 'magischer Wald', 'Weltraumstation', 'Unterwasserstadt'.",
        ),
        (
            "de",
            "CONTENT_INAPPROPRIATE",
            "❌ Diese Beschreibung ist nicht für eine Kindergeschichte geeignet. Versuchen Sie etwas Kindgerechteres.",
        ),
        ("de", "STORY_PARAMETERS_READY", "🎉 Perfekt! Die Parameter Ihrer Geschichte sind bereit:"),
    ]

    op.execute("DELETE FROM phrase_translation")
    for language_code, phrase_enum, translation in phrase_translations:
        translation = translation.replace("'", "''")
        op.execute(
            f"INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES ('{language_code}', '{phrase_enum}', '{translation}')"
        )


def downgrade() -> None:
    # Remove all phrase translations
    op.execute("DELETE FROM phrase_translation")
