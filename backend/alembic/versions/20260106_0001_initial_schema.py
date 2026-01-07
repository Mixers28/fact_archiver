"""initial schema

Revision ID: 20260106_0001
Revises:
Create Date: 2026-01-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260106_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "source_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "discovered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("fetch_headers", postgresql.JSONB(), nullable=True),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("language", sa.String(length=32), nullable=True),
        sa.Column("capture_tier", sa.Integer(), nullable=False),
        sa.Column("capture_status", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("bytes", sa.Integer(), nullable=True),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("tool_version", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["source_item_id"], ["source_items.id"]),
    )

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("date_key", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("importance_score", sa.Float(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        "event_memberships",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["source_item_id"], ["source_items.id"]),
        sa.PrimaryKeyConstraint("event_id", "source_item_id"),
    )

    op.create_table(
        "claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("claim_type", sa.String(length=32), nullable=False),
        sa.Column("entities", postgresql.JSONB(), nullable=True),
        sa.Column("numeric_fields", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
    )

    op.create_table(
        "claim_assertions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("extracted_span", sa.String(length=64), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("polarity", sa.String(length=16), nullable=False),
        sa.Column("assertion_time", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"]),
        sa.ForeignKeyConstraint(["source_item_id"], ["source_items.id"]),
    )

    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("rationale", postgresql.JSONB(), nullable=True),
        sa.Column("computed_signals", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"]),
    )

    op.create_table(
        "transparency_log_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("previous_root", sa.String(length=128), nullable=True),
        sa.Column("merkle_root", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade():
    op.drop_table("transparency_log_entries")
    op.drop_table("assessments")
    op.drop_table("claim_assertions")
    op.drop_table("claims")
    op.drop_table("event_memberships")
    op.drop_table("events")
    op.drop_table("artifacts")
    op.drop_table("source_items")
