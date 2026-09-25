"""Identity: branches, user_profiles, user_branch_assignments

Revision ID: 0001_identity
Revises:
Create Date: 2026-09-13

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_identity"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_IDENTITY_TABLES = ("branches", "user_profiles", "user_branch_assignments")


def _revoke_direct_api_access() -> None:
    """Supabase expone la API REST directa a anon/authenticated; el backend es
    privado, así que se revocan todos los privilegios (si los roles existen)."""
    tables = ", ".join(f"public.{table}" for table in _IDENTITY_TABLES)
    for role in ("anon", "authenticated"):
        op.execute(
            f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                    REVOKE ALL PRIVILEGES ON TABLE {tables} FROM {role};
                END IF;
            END
            $$
            """
        )


def upgrade() -> None:
    role_enum = sa.Enum("admin", "encargado", "vendedor", name="user_role")
    op.create_table(
        "branches",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index(op.f("ix_branches_code"), "branches", ["code"], unique=True)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("email = lower(email)", name="ck_user_profiles_email_lowercase"),
    )
    op.create_index(op.f("ix_user_profiles_email"), "user_profiles", ["email"], unique=True)

    op.create_table(
        "user_branch_assignments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "branch_id", name="uq_user_branch"),
    )
    op.create_index(
        op.f("ix_user_branch_assignments_user_id"),
        "user_branch_assignments",
        ["user_id"],
    )
    op.create_index(
        op.f("ix_user_branch_assignments_branch_id"),
        "user_branch_assignments",
        ["branch_id"],
    )

    for table in _IDENTITY_TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
    _revoke_direct_api_access()


def downgrade() -> None:
    # RLS y privilegios desaparecen junto con las tablas.
    op.drop_table("user_branch_assignments")
    op.drop_table("user_profiles")
    op.drop_table("branches")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
