"""initial life platform schema

Revision ID: 0001_initial_life_schema
Revises:
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_life_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "domains",
        sa.Column("key", sa.String(length=32), primary_key=True),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("api_base", sa.String(length=512), nullable=False),
        sa.Column("homepage_url", sa.String(length=512), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_domains_category", "domains", ["category"])

    op.create_table(
        "domain_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain_key", sa.String(length=32), sa.ForeignKey("domains.key"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("health_score", sa.Float(), nullable=False),
        sa.Column("summary", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("highlights", sa.JSON(), nullable=False),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_domain_snapshots_domain_key", "domain_snapshots", ["domain_key"])
    op.create_index("ix_domain_snapshots_observed_at", "domain_snapshots", ["observed_at"])
    op.create_index("ix_domain_snapshots_status", "domain_snapshots", ["status"])

    op.create_table(
        "life_index_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile", sa.String(length=32), nullable=False),
        sa.Column("district", sa.String(length=128), nullable=False),
        sa.Column("total_lkr", sa.Float(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("breakdown", sa.JSON(), nullable=False),
        sa.Column("assumptions", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_life_index_snapshots_profile", "life_index_snapshots", ["profile"])
    op.create_index("ix_life_index_snapshots_district", "life_index_snapshots", ["district"])
    op.create_index("ix_life_index_snapshots_observed_at", "life_index_snapshots", ["observed_at"])

    op.create_table(
        "integration_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain_key", sa.String(length=32), sa.ForeignKey("domains.key"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload_summary", sa.JSON(), nullable=True),
    )
    op.create_index("ix_integration_runs_domain_key", "integration_runs", ["domain_key"])
    op.create_index("ix_integration_runs_status", "integration_runs", ["status"])
    op.create_index("ix_integration_runs_started_at", "integration_runs", ["started_at"])


def downgrade() -> None:
    op.drop_table("integration_runs")
    op.drop_table("life_index_snapshots")
    op.drop_table("domain_snapshots")
    op.drop_table("domains")
