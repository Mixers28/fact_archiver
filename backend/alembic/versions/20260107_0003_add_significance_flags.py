"""add significance flags

Revision ID: 20260107_0003
Revises: 20260106_0002
Create Date: 2026-01-07 00:03:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "20260107_0003"
down_revision = "20260106_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("source_items", sa.Column("is_significant", sa.Boolean(), nullable=True))
    op.add_column(
        "source_items",
        sa.Column("is_filtered", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("source_items", "is_filtered")
    op.drop_column("source_items", "is_significant")
