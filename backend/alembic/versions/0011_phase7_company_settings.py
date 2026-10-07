"""Add persistent single-company profile settings.

Revision ID: 0011_phase7_company_settings
Revises: 0010_phase6_repair_sales
Create Date: 2026-09-27
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0011_phase7_company_settings"
down_revision: str | None = "0010_phase6_repair_sales"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_name", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("rfc", sa.String(length=13), nullable=False, server_default=""),
        sa.Column("fiscal_address", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("phone", sa.String(length=10), nullable=False, server_default=""),
        sa.Column("email", sa.String(length=255), nullable=False, server_default=""),
        sa.CheckConstraint("id = 1", name="ck_company_settings_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("ALTER TABLE public.company_settings ENABLE ROW LEVEL SECURITY")
    for role in ("anon", "authenticated"):
        op.execute(
            f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                    REVOKE ALL PRIVILEGES ON TABLE public.company_settings FROM {role};
                END IF;
            END
            $$
            """
        )


def downgrade() -> None:
    op.drop_table("company_settings")
