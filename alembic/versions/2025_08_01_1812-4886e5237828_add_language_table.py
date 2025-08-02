"""Add language table

Revision ID: 4886e5237828
Revises: 1c444ce35e6c
Create Date: 2025-08-01 18:12:14.524417

"""

# pylint: disable=all
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4886e5237828"
down_revision = "1c444ce35e6c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "language",
        sa.Column("language_code", sa.String(length=10), nullable=False),
        sa.Column(
            "user_language_code", sa.String(length=10), nullable=False
        ),
        sa.Column("word", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("language_code", "user_language_code"),
    )
    
    # Fill the language table with language names in different languages
    language_data = [
        # English names
        ("en", "en", "English"),
        ("ru", "en", "Russian"),
        ("es", "en", "Spanish"),
        ("it", "en", "Italian"),
        ("fr", "en", "French"),
        ("be", "en", "Belarusian"),
        ("uk", "en", "Ukrainian"),
        
        # Russian names
        ("en", "ru", "Английский"),
        ("ru", "ru", "Русский"),
        ("es", "ru", "Испанский"),
        ("it", "ru", "Итальянский"),
        ("fr", "ru", "Французский"),
        ("be", "ru", "Беларусский"),
        ("uk", "ru", "Украинский"),
        
        # Spanish names
        ("en", "es", "Inglés"),
        ("ru", "es", "Ruso"),
        ("es", "es", "Español"),
        ("it", "es", "Italiano"),
        ("fr", "es", "Francés"),
        ("be", "es", "Bielorruso"),
        ("uk", "es", "Ucraniano"),
        
        # Italian names
        ("en", "it", "Inglese"),
        ("ru", "it", "Russo"),
        ("es", "it", "Spagnolo"),
        ("it", "it", "Italiano"),
        ("fr", "it", "Francese"),
        ("be", "it", "Bielorusso"),
        ("uk", "it", "Ucraino"),
        
        # French names
        ("en", "fr", "Anglais"),
        ("ru", "fr", "Russe"),
        ("es", "fr", "Espagnol"),
        ("it", "fr", "Italien"),
        ("fr", "fr", "Français"),
        ("be", "fr", "Biélorusse"),
        ("uk", "fr", "Ukrainien"),
        
        # Belarusian names
        ("en", "be", "Англійская"),
        ("ru", "be", "Руская"),
        ("es", "be", "Іспанская"),
        ("it", "be", "Італьянская"),
        ("fr", "be", "Французская"),
        ("be", "be", "Беларуская"),
        ("uk", "be", "Украінская"),
        
        # Ukrainian names
        ("en", "uk", "Англійська"),
        ("ru", "uk", "Російська"),
        ("es", "uk", "Іспанська"),
        ("it", "uk", "Італійська"),
        ("fr", "uk", "Французька"),
        ("be", "uk", "Білоруська"),
        ("uk", "uk", "Українська"),
    ]
    
    for language_code, user_language_code, word in language_data:
        op.execute(
            f"INSERT INTO language (language_code, user_language_code, word) VALUES ('{language_code}', '{user_language_code}', '{word}')"
        )


def downgrade() -> None:
    op.drop_table("language")
