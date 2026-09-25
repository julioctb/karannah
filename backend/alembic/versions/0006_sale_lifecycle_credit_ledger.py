"""Sale lifecycle, credit branch traceability and reversible financial entries.

Revision ID: 0006_sale_lifecycle_credit_ledger
Revises: 0005_phase4_pos
Create Date: 2026-09-22
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006_sale_lifecycle_credit_ledger"
down_revision: str | None = "0005_phase4_pos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    sale_status = postgresql.ENUM("confirmada", "cancelada", name="sale_status")
    sale_status.create(op.get_bind(), checkfirst=True)

    op.execute("ALTER TYPE cash_movement_type ADD VALUE IF NOT EXISTS 'cancelacion_venta'")

    op.add_column(
        "sales",
        sa.Column(
            "status",
            postgresql.ENUM(name="sale_status", create_type=False),
            server_default="confirmada",
            nullable=False,
        ),
    )
    op.add_column("sales", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sales", sa.Column("cancelled_by", sa.Uuid(), nullable=True))
    op.add_column("sales", sa.Column("cancellation_reason", sa.String(255), nullable=True))
    op.create_foreign_key(
        "fk_sales_cancelled_by",
        "sales",
        "user_profiles",
        ["cancelled_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_sales_cancelled_by", "sales", ["cancelled_by"])

    op.add_column("credit_entries", sa.Column("branch_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_credit_entries_branch",
        "credit_entries",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_credit_entries_branch_id", "credit_entries", ["branch_id"])
    op.execute(
        """
        UPDATE credit_entries c
        SET branch_id = s.branch_id
        FROM sales s
        WHERE c.sale_id = s.id AND c.branch_id IS NULL
        """
    )

    op.drop_constraint("ck_cash_movements_amount_positive", "cash_movements", type_="check")
    op.create_check_constraint(
        "ck_cash_movements_amount_nonzero", "cash_movements", "amount <> 0"
    )
    op.drop_constraint("ck_payments_amount_positive", "payments", type_="check")
    op.create_check_constraint("ck_payments_amount_nonzero", "payments", "amount <> 0")


def downgrade() -> None:
    op.drop_constraint("ck_payments_amount_nonzero", "payments", type_="check")
    op.create_check_constraint("ck_payments_amount_positive", "payments", "amount > 0")
    op.drop_constraint("ck_cash_movements_amount_nonzero", "cash_movements", type_="check")
    op.create_check_constraint(
        "ck_cash_movements_amount_positive", "cash_movements", "amount > 0"
    )

    op.drop_index("ix_credit_entries_branch_id", table_name="credit_entries")
    op.drop_constraint("fk_credit_entries_branch", "credit_entries", type_="foreignkey")
    op.drop_column("credit_entries", "branch_id")

    op.drop_index("ix_sales_cancelled_by", table_name="sales")
    op.drop_constraint("fk_sales_cancelled_by", "sales", type_="foreignkey")
    op.drop_column("sales", "cancellation_reason")
    op.drop_column("sales", "cancelled_by")
    op.drop_column("sales", "cancelled_at")
    op.drop_column("sales", "status")

    sale_status = postgresql.ENUM(name="sale_status")
    sale_status.drop(op.get_bind(), checkfirst=True)
