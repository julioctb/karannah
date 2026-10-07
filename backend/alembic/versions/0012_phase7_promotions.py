"""Add global cart-wide percentage promotions.

Revision ID: 0012_phase7_promotions
Revises: 0011_phase7_company_settings
Create Date: 2026-10-07
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0012_phase7_promotions"
down_revision: str | None = "0011_phase7_company_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "promotions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("discount_percent", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=True),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "discount_percent > 0 AND discount_percent <= 100",
            name="ck_promotions_discount_percent",
        ),
        sa.CheckConstraint(
            "starts_on IS NULL OR ends_on IS NULL OR starts_on <= ends_on",
            name="ck_promotions_date_range",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_promotions_active", "promotions", ["active"])
    op.add_column("sales", sa.Column("promotion_id", sa.Integer(), nullable=True))
    op.add_column("sales", sa.Column("promotion_name", sa.String(length=160), nullable=True))
    op.create_foreign_key(
        "fk_sales_promotion_id",
        "sales",
        "promotions",
        ["promotion_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_sales_promotion_id", "sales", ["promotion_id"])
    op.create_check_constraint(
        "ck_sales_promotion_attribution",
        "sales",
        "(promotion_id IS NULL AND promotion_name IS NULL) OR "
        "(promotion_id IS NOT NULL AND promotion_name IS NOT NULL)",
    )
    op.execute("ALTER TABLE public.promotions ENABLE ROW LEVEL SECURITY")
    for role in ("anon", "authenticated"):
        op.execute(
            f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                    REVOKE ALL PRIVILEGES ON TABLE public.promotions FROM {role};
                END IF;
            END
            $$
            """
        )


def downgrade() -> None:
    op.drop_constraint("ck_sales_promotion_attribution", "sales", type_="check")
    op.drop_index("ix_sales_promotion_id", table_name="sales")
    op.drop_constraint("fk_sales_promotion_id", "sales", type_="foreignkey")
    op.drop_column("sales", "promotion_name")
    op.drop_column("sales", "promotion_id")
    op.drop_index("ix_promotions_active", table_name="promotions")
    op.drop_table("promotions")
