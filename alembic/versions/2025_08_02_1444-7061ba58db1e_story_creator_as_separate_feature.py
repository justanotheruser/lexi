"""Story creator as separate feature

Revision ID: 7061ba58db1e
Revises: d05d790841dc
Create Date: 2025-08-02 14:44:56.886465

"""

import sqlalchemy as sa
import sqlmodel

# pylint: disable=all
from alembic import op

# revision identifiers, used by Alembic.
revision = "7061ba58db1e"
down_revision = "d05d790841dc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "language__user_language_code_fk",
        "language",
        "supported_user_language",
        ["user_language_code"],
        ["language_code"],
    )
    op.create_foreign_key(
        "language__language_code_fk",
        "language",
        "supported_story_language",
        ["language_code"],
        ["language_code"],
    )


def downgrade() -> None:
    op.drop_constraint("language__user_language_code_fk", "language", type_="foreignkey")
    op.drop_constraint("language__language_code_fk", "language", type_="foreignkey")
