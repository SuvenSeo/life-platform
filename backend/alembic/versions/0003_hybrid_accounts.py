"""hybrid account schema

Revision ID: 0003_hybrid_accounts
Revises: 0002_living_atlas_schema
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_hybrid_accounts"
down_revision = "0002_living_atlas_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("auth_sub", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=160), nullable=True),
        sa.Column("photo_url", sa.String(length=512), nullable=True),
        sa.Column("default_locale", sa.String(length=8), nullable=False),
        sa.Column("district", sa.String(length=128), nullable=False),
        sa.Column("profile", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_profiles_auth_sub", "user_profiles", ["auth_sub"], unique=True)

    op.create_table(
        "saved_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("auth_sub", sa.String(length=160), nullable=False),
        sa.Column("domain_key", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=180), nullable=False),
        sa.Column("query", sa.String(length=160), nullable=True),
        sa.Column("href", sa.String(length=512), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_saved_items_auth_sub", "saved_items", ["auth_sub"])
    op.create_index("ix_saved_items_domain_key", "saved_items", ["domain_key"])
    op.create_index("ix_saved_items_created_at", "saved_items", ["created_at"])

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("auth_sub", sa.String(length=160), nullable=False),
        sa.Column("domain_key", sa.String(length=32), nullable=True),
        sa.Column("label", sa.String(length=180), nullable=False),
        sa.Column("metric_label", sa.String(length=120), nullable=True),
        sa.Column("condition", sa.String(length=40), nullable=False),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_alert_rules_auth_sub", "alert_rules", ["auth_sub"])
    op.create_index("ix_alert_rules_domain_key", "alert_rules", ["domain_key"])
    op.create_index("ix_alert_rules_condition", "alert_rules", ["condition"])
    op.create_index("ix_alert_rules_enabled", "alert_rules", ["enabled"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("auth_sub", sa.String(length=160), nullable=False),
        sa.Column("alert_rule_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("source_domain", sa.String(length=32), nullable=True),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("auth_sub", "idempotency_key", name="uq_notifications_auth_idempotency"),
    )
    op.create_index("ix_notifications_auth_sub", "notifications", ["auth_sub"])
    op.create_index("ix_notifications_alert_rule_id", "notifications", ["alert_rule_id"])
    op.create_index("ix_notifications_severity", "notifications", ["severity"])
    op.create_index("ix_notifications_source_domain", "notifications", ["source_domain"])
    op.create_index("ix_notifications_read_at", "notifications", ["read_at"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("alert_rules")
    op.drop_table("saved_items")
    op.drop_table("user_profiles")
