"""Phase 5 physical-count (CF) document foundations.

Revision ID: 0008_phase5_physical_counts
Revises: 0007_phase5_transfers
Create Date: 2026-09-24
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0008_phase5_physical_counts"
down_revision: str | None = "0007_phase5_transfers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    count_status = postgresql.ENUM(
        "open", "finalized", name="physical_count_status", create_type=False
    )
    count_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "physical_counts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("folio", sa.String(30), nullable=False),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", count_status, server_default="open", nullable=False),
        sa.Column(
            "created_by",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "finalized_by",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("folio LIKE 'CF-%'", name="ck_physical_counts_folio_prefix"),
    )
    op.create_index("ix_physical_counts_folio", "physical_counts", ["folio"], unique=True)
    op.create_index("ix_physical_counts_branch_id", "physical_counts", ["branch_id"])
    op.create_index("ix_physical_counts_status", "physical_counts", ["status"])
    op.create_index("ix_physical_counts_created_by", "physical_counts", ["created_by"])
    op.create_index("ix_physical_counts_created_at", "physical_counts", ["created_at"])

    op.create_table(
        "physical_count_lines",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "physical_count_id",
            sa.Uuid(),
            sa.ForeignKey("physical_counts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "variant_id",
            sa.Integer(),
            sa.ForeignKey("product_variants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("snapshot_quantity", sa.Integer(), nullable=False),
        sa.Column("observed_quantity", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "snapshot_quantity >= 0",
            name="ck_physical_count_lines_snapshot_quantity_nonnegative",
        ),
        sa.CheckConstraint(
            "observed_quantity IS NULL OR observed_quantity >= 0",
            name="ck_physical_count_lines_observed_quantity_nonnegative",
        ),
        sa.UniqueConstraint(
            "physical_count_id",
            "variant_id",
            name="uq_physical_count_lines_physical_count_variant",
        ),
    )
    op.create_index(
        "ix_physical_count_lines_physical_count_id",
        "physical_count_lines",
        ["physical_count_id"],
    )
    op.create_index(
        "ix_physical_count_lines_variant_id", "physical_count_lines", ["variant_id"]
    )

    for table in ("physical_counts", "physical_count_lines"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                REVOKE ALL PRIVILEGES ON TABLE physical_counts, physical_count_lines FROM anon;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                REVOKE ALL PRIVILEGES ON TABLE physical_counts, physical_count_lines
                    FROM authenticated;
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.drop_table("physical_count_lines")
    op.drop_table("physical_counts")

    postgresql.ENUM(name="physical_count_status").drop(op.get_bind(), checkfirst=True)
