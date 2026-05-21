"""living atlas public source schema

Revision ID: 0002_living_atlas_schema
Revises: 0001_initial_life_schema
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_living_atlas_schema"
down_revision = "0001_initial_life_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_registry",
        sa.Column("key", sa.String(length=80), primary_key=True),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("domain_key", sa.String(length=32), nullable=True),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("freshness_note", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("locale_labels", sa.JSON(), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_registry_source_type", "source_registry", ["source_type"])
    op.create_index("ix_source_registry_domain_key", "source_registry", ["domain_key"])
    op.create_index("ix_source_registry_status", "source_registry", ["status"])

    op.create_table(
        "tariff_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain_key", sa.String(length=32), nullable=False),
        sa.Column("source_key", sa.String(length=80), sa.ForeignKey("source_registry.key"), nullable=False),
        sa.Column("district", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("amount_lkr", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tariff_snapshots_domain_key", "tariff_snapshots", ["domain_key"])
    op.create_index("ix_tariff_snapshots_source_key", "tariff_snapshots", ["source_key"])
    op.create_index("ix_tariff_snapshots_district", "tariff_snapshots", ["district"])
    op.create_index("ix_tariff_snapshots_category", "tariff_snapshots", ["category"])
    op.create_index("ix_tariff_snapshots_observed_at", "tariff_snapshots", ["observed_at"])

    op.create_table(
        "retail_offer_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_key", sa.String(length=80), sa.ForeignKey("source_registry.key"), nullable=False),
        sa.Column("item_name", sa.String(length=160), nullable=False),
        sa.Column("retailer", sa.String(length=120), nullable=False),
        sa.Column("district", sa.String(length=128), nullable=False),
        sa.Column("price_lkr", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_retail_offer_snapshots_source_key", "retail_offer_snapshots", ["source_key"])
    op.create_index("ix_retail_offer_snapshots_item_name", "retail_offer_snapshots", ["item_name"])
    op.create_index("ix_retail_offer_snapshots_retailer", "retail_offer_snapshots", ["retailer"])
    op.create_index("ix_retail_offer_snapshots_district", "retail_offer_snapshots", ["district"])
    op.create_index("ix_retail_offer_snapshots_observed_at", "retail_offer_snapshots", ["observed_at"])

    op.create_table(
        "transport_fare_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_key", sa.String(length=80), sa.ForeignKey("source_registry.key"), nullable=False),
        sa.Column("mode", sa.String(length=64), nullable=False),
        sa.Column("from_area", sa.String(length=128), nullable=False),
        sa.Column("to_area", sa.String(length=128), nullable=False),
        sa.Column("fare_lkr", sa.Float(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transport_fare_snapshots_source_key", "transport_fare_snapshots", ["source_key"])
    op.create_index("ix_transport_fare_snapshots_mode", "transport_fare_snapshots", ["mode"])
    op.create_index("ix_transport_fare_snapshots_from_area", "transport_fare_snapshots", ["from_area"])
    op.create_index("ix_transport_fare_snapshots_to_area", "transport_fare_snapshots", ["to_area"])
    op.create_index("ix_transport_fare_snapshots_observed_at", "transport_fare_snapshots", ["observed_at"])

    op.create_table(
        "area_score_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("district", sa.String(length=128), nullable=False),
        sa.Column("profile", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("grade", sa.String(length=8), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("components", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_area_score_snapshots_district", "area_score_snapshots", ["district"])
    op.create_index("ix_area_score_snapshots_profile", "area_score_snapshots", ["profile"])
    op.create_index("ix_area_score_snapshots_observed_at", "area_score_snapshots", ["observed_at"])

    op.create_table(
        "public_insight_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("insight_key", sa.String(length=120), nullable=False),
        sa.Column("domain_key", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("source_keys", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_public_insight_snapshots_insight_key", "public_insight_snapshots", ["insight_key"])
    op.create_index("ix_public_insight_snapshots_domain_key", "public_insight_snapshots", ["domain_key"])
    op.create_index("ix_public_insight_snapshots_severity", "public_insight_snapshots", ["severity"])
    op.create_index("ix_public_insight_snapshots_observed_at", "public_insight_snapshots", ["observed_at"])


def downgrade() -> None:
    op.drop_table("public_insight_snapshots")
    op.drop_table("area_score_snapshots")
    op.drop_table("transport_fare_snapshots")
    op.drop_table("retail_offer_snapshots")
    op.drop_table("tariff_snapshots")
    op.drop_table("source_registry")
