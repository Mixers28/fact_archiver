"""phase 3 processing tables

Revision ID: 20260106_0002
Revises: 20260106_0001
Create Date: 2026-01-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260106_0002"
down_revision = "20260106_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("source_items", sa.Column("title", sa.Text(), nullable=True))

    op.create_table(
        "normalized_texts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_item_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("canonical_source_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("text_hash", sa.String(length=64), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["source_item_id"], ["source_items.id"]),
        sa.ForeignKeyConstraint(["canonical_source_item_id"], ["source_items.id"]),
    )
    op.create_index(
        "ix_normalized_texts_text_hash",
        "normalized_texts",
        ["text_hash"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_normalized_texts_text_hash", table_name="normalized_texts")
    op.drop_table("normalized_texts")
    op.drop_column("source_items", "title")
