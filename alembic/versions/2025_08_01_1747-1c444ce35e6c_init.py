"""Init

Revision ID: 1c444ce35e6c
Revises:
Create Date: 2025-08-01 17:47:10.748995

"""

# pylint: disable=all

import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "1c444ce35e6c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supported_story_language",
        sa.Column("language_code", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.PrimaryKeyConstraint("language_code"),
    )
    op.create_table(
        "supported_user_language",
        sa.Column("language_code", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.PrimaryKeyConstraint("language_code"),
    )
    op.execute(
        "INSERT INTO supported_story_language (language_code) VALUES ('en'), ('ru'), ('es'), ('it'), ('fr'), ('be'), ('uk'), ('de')"
    )
    op.execute(
        "INSERT INTO supported_user_language (language_code) VALUES ('en'), ('ru'), ('es'), ('it'), ('fr'), ('be'), ('uk'), ('de')"
    )


def downgrade() -> None:
    op.drop_table("supported_user_language")
    op.drop_table("supported_story_language")
