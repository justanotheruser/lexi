"""Phrase translations in DB

Revision ID: d05d790841dc
Revises: 1689c313cf6c
Create Date: 2025-08-02 14:13:40.602276

"""

import sqlalchemy as sa
from sqlalchemy import String

# pylint: disable=all
from alembic import op

# revision identifiers, used by Alembic.
revision = "d05d790841dc"
down_revision = "1689c313cf6c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "phrase_translation",
        sa.Column("language_code", String(length=10), nullable=False),
        sa.Column("phrase_enum", sa.Text(), nullable=False),
        sa.Column("translation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["language_code"],
            ["supported_user_language.language_code"],
        ),
        sa.PrimaryKeyConstraint("language_code", "phrase_enum"),
    )

    # Insert phrase translations from i18n.py
    # Russian translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('ru', 'WHAT_LANGUAGE_YOU_WANT_LEARN', 'Какой язык вы хотите изучать?'),
        ('ru', 'LETS_LEARN', '✅ Хорошо, давайте изучать <b>${language_name}</b>!'),
        ('ru', 'LANGUAGE_NOT_SUPPORTED', '❌ Язык не поддерживается. Попробуйте снова с поддерживаемым языком.'),
        ('ru', 'WELCOME', '👋 Добро пожаловать! Я помогу вам изучать языки.')
    """
    )

    # English translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('en', 'WHAT_LANGUAGE_YOU_WANT_LEARN', 'What language would you like to learn?'),
        ('en', 'LETS_LEARN', '✅ Ok, let''s learn <b>${language_name}</b>!'),
        ('en', 'LANGUAGE_NOT_SUPPORTED', '❌ Language not supported. Please try again with a supported language.'),
        ('en', 'WELCOME', '👋 Welcome! I''ll help you learn languages.')
    """
    )

    # Spanish translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('es', 'WHAT_LANGUAGE_YOU_WANT_LEARN', '¿Qué idioma te gustaría aprender?'),
        ('es', 'LETS_LEARN', '✅ Ok, vamos a aprender <b>${language_name}</b>!'),
        ('es', 'LANGUAGE_NOT_SUPPORTED', '❌ Idioma no soportado. Inténtalo de nuevo con un idioma soportado.'),
        ('es', 'WELCOME', '👋 ¡Bienvenido! Te ayudaré a aprender idiomas.')
    """
    )

    # French translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('fr', 'WHAT_LANGUAGE_YOU_WANT_LEARN', 'Quelle langue voulez-vous apprendre?'),
        ('fr', 'LETS_LEARN', '✅ Ok, apprenons <b>${language_name}</b>!'),
        ('fr', 'LANGUAGE_NOT_SUPPORTED', '❌ Langue non prise en charge. Veuillez réessayer avec une langue prise en charge.'),
        ('fr', 'WELCOME', '👋 Bienvenue! Je vous aiderai à apprendre les langues.')
    """
    )

    # German translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('de', 'WHAT_LANGUAGE_YOU_WANT_LEARN', 'Welche Sprache möchten Sie lernen?'),
        ('de', 'LETS_LEARN', '✅ Ok, lass uns <b>${language_name}</b> lernen!'),
        ('de', 'LANGUAGE_NOT_SUPPORTED', '❌ Sprache wird nicht unterstützt. Bitte versuchen Sie es erneut mit einer unterstützten Sprache.'),
        ('de', 'WELCOME', '👋 Willkommen! Ich helfe Ihnen beim Sprachenlernen.')
        """
    )

    # Italian translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('it', 'WHAT_LANGUAGE_YOU_WANT_LEARN', 'Che lingua vorresti imparare?'),
        ('it', 'LETS_LEARN', '✅ Ok, impariamo <b>${language_name}</b>!'),
        ('it', 'LANGUAGE_NOT_SUPPORTED', '❌ Lingua non supportata. Riprova con una lingua supportata.'),
        ('it', 'WELCOME', '👋 Benvenuto! Ti aiuterò a imparare le lingue.')
        """
    )

    # Belarusian translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('be', 'WHAT_LANGUAGE_YOU_WANT_LEARN', 'Якую мову вы хочаце вывучаць?'),
        ('be', 'LETS_LEARN', '✅ Добра, давайце вывучаць <b>${language_name}</b>!'),
        ('be', 'LANGUAGE_NOT_SUPPORTED', '❌ Мова не падтрымліваецца. Паспрабуйце зноў з падтрымліваемай мовай.'),
        ('be', 'WELCOME', '👋 Сардэчна запрашаем! Я дапамагу вам вывучаць мовы.')
        """
    )

    # Ukrainian translations
    op.execute(
        """
        INSERT INTO phrase_translation (language_code, phrase_enum, translation) VALUES
        ('uk', 'WHAT_LANGUAGE_YOU_WANT_LEARN', 'Яку мову ви хочете вивчати?'),
        ('uk', 'LETS_LEARN', '✅ Добре, давайте вивчати <b>${language_name}</b>!'),
        ('uk', 'LANGUAGE_NOT_SUPPORTED', '❌ Мова не підтримується. Спробуйте знову з підтримуваною мовою.'),
        ('uk', 'WELCOME', '👋 Ласкаво просимо! Я допоможу вам вивчати мови.')
        """
    )


def downgrade() -> None:
    op.drop_table("phrase_translation")
