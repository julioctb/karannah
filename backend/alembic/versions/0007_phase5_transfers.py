"""Phase 5 transfer (TR) document foundations.

Revision ID: 0007_phase5_transfers
Revises: 0006_sale_lifecycle_credit_ledger
Create Date: 2026-09-24
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0007_phase5_transfers"
down_revision: str | None = "0006_sale_lifecycle_credit_ledger"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    transfer_status = postgresql.ENUM(
        "draft", "sent", "received", name="stock_transfer_status", create_type=False
    )
    transfer_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "stock_transfers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("folio", sa.String(30), nullable=False),
        sa.Column(
            "origin_branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "destination_branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", transfer_status, server_default="draft", nullable=False),
        sa.Column(
            "created_by",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "sent_by",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "received_by",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("folio LIKE 'TR-%'", name="ck_stock_transfers_folio_prefix"),
        sa.CheckConstraint(
            "origin_branch_id <> destination_branch_id",
            name="ck_stock_transfers_distinct_branches",
        ),
    )
    op.create_index("ix_stock_transfers_folio", "stock_transfers", ["folio"], unique=True)
    op.create_index(
        "ix_stock_transfers_origin_branch_id", "stock_transfers", ["origin_branch_id"]
    )
    op.create_index(
        "ix_stock_transfers_destination_branch_id",
        "stock_transfers",
        ["destination_branch_id"],
    )
    op.create_index("ix_stock_transfers_status", "stock_transfers", ["status"])
    op.create_index("ix_stock_transfers_created_by", "stock_transfers", ["created_by"])
    op.create_index("ix_stock_transfers_created_at", "stock_transfers", ["created_at"])

    op.create_table(
        "stock_transfer_lines",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "transfer_id",
            sa.Uuid(),
            sa.ForeignKey("stock_transfers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "variant_id",
            sa.Integer(),
            sa.ForeignKey("product_variants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("shipped_quantity", sa.Integer(), nullable=False),
        sa.Column("received_quantity", sa.Integer(), nullable=True),
        sa.Column("shortage_quantity", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "shipped_quantity > 0",
            name="ck_stock_transfer_lines_shipped_quantity_positive",
        ),
        sa.CheckConstraint(
            "received_quantity IS NULL OR received_quantity >= 0",
            name="ck_stock_transfer_lines_received_quantity_nonnegative",
        ),
        sa.CheckConstraint(
            "shortage_quantity IS NULL OR shortage_quantity >= 0",
            name="ck_stock_transfer_lines_shortage_quantity_nonnegative",
        ),
        sa.CheckConstraint(
            "received_quantity IS NULL OR received_quantity <= shipped_quantity",
            name="ck_stock_transfer_lines_received_not_over_shipped",
        ),
        sa.CheckConstraint(
            "(received_quantity IS NULL AND shortage_quantity IS NULL) OR "
            "(received_quantity IS NOT NULL AND shortage_quantity IS NOT NULL AND "
            "shortage_quantity = shipped_quantity - received_quantity)",
            name="ck_stock_transfer_lines_shortage_matches_received",
        ),
        sa.UniqueConstraint(
            "transfer_id", "variant_id", name="uq_stock_transfer_line_variant"
        ),
    )
    op.create_index(
        "ix_stock_transfer_lines_transfer_id", "stock_transfer_lines", ["transfer_id"]
    )
    op.create_index(
        "ix_stock_transfer_lines_variant_id", "stock_transfer_lines", ["variant_id"]
    )

    for table in ("stock_transfers", "stock_transfer_lines"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                REVOKE ALL PRIVILEGES ON TABLE stock_transfers, stock_transfer_lines FROM anon;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                REVOKE ALL PRIVILEGES ON TABLE stock_transfers, stock_transfer_lines
                    FROM authenticated;
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.drop_table("stock_transfer_lines")
    op.drop_table("stock_transfers")

    postgresql.ENUM(name="stock_transfer_status").drop(op.get_bind(), checkfirst=True)
