"""Add inventory-free sale lines for repair services.

Revision ID: 0010_phase6_repair_sales
Revises: 0009_phase6_repairs
Create Date: 2026-09-26
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010_phase6_repair_sales"
down_revision: str | None = "0009_phase6_repairs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("sale_items", "variant_id", nullable=True)
    op.add_column("sale_items", sa.Column("repair_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_sale_items_repair_id",
        "sale_items",
        "repairs",
        ["repair_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_sale_items_repair_id", "sale_items", ["repair_id"])
    op.create_unique_constraint("uq_sale_items_repair_id", "sale_items", ["repair_id"])
    op.create_check_constraint(
        "ck_sale_items_single_line_source",
        "sale_items",
        "(variant_id IS NOT NULL AND repair_id IS NULL) OR "
        "(variant_id IS NULL AND repair_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_sale_items_single_line_source", "sale_items", type_="check"
    )
    op.drop_constraint("uq_sale_items_repair_id", "sale_items", type_="unique")
    op.drop_index("ix_sale_items_repair_id", table_name="sale_items")
    op.drop_constraint("fk_sale_items_repair_id", "sale_items", type_="foreignkey")
    op.drop_column("sale_items", "repair_id")
    op.alter_column("sale_items", "variant_id", nullable=False)
