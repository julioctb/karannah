"""Phase 6 repair workflow foundations.

Revision ID: 0009_phase6_repairs
Revises: 0008_phase5_physical_counts
Create Date: 2026-09-25
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0009_phase6_repairs"
down_revision: str | None = "0008_phase5_physical_counts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PHASE6_STATUSES = ("received", "in_workshop", "ready")


def upgrade() -> None:
    # PostgreSQL enum values cannot be removed in place. Convert through text so
    # legacy rows collapse into the deliberately smaller Phase 6 vocabulary.
    op.execute("ALTER TABLE repairs ALTER COLUMN status TYPE VARCHAR USING status::text")
    op.execute(
        """
        UPDATE repairs
        SET status = CASE status
            WHEN 'recibido' THEN 'received'
            WHEN 'terminado' THEN 'ready'
            ELSE 'in_workshop'
        END
        """
    )
    op.execute("DROP TYPE repair_status")
    repair_status = postgresql.ENUM(*_PHASE6_STATUSES, name="repair_status", create_type=False)
    repair_status.create(op.get_bind(), checkfirst=True)
    op.execute(
        "ALTER TABLE repairs ALTER COLUMN status TYPE repair_status "
        "USING status::repair_status"
    )
    op.alter_column("repairs", "status", server_default="received")

    op.drop_constraint("ck_repairs_quoted_price_nonnegative", "repairs", type_="check")
    op.execute("ALTER TABLE repairs RENAME COLUMN quoted_price TO price")
    op.create_check_constraint(
        "ck_repairs_price_nonnegative", "repairs", "price IS NULL OR price >= 0"
    )
    # Existing pre-Phase-6 demo repairs retain R-* folios; all new intake uses RP-*.
    op.create_check_constraint(
        "ck_repairs_folio_prefix",
        "repairs",
        "folio LIKE 'RP-%' OR folio LIKE 'R-%'",
    )

    op.add_column("repairs", sa.Column("branch_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_repairs_branch_id",
        "repairs",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_repairs_branch_id", "repairs", ["branch_id"])

    op.add_column("repairs", sa.Column("sale_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_repairs_sale_id",
        "repairs",
        "sales",
        ["sale_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint("uq_repairs_sale_id", "repairs", ["sale_id"])
    op.create_index("ix_repairs_sale_id", "repairs", ["sale_id"])
    op.add_column(
        "repairs", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "repairs",
        sa.Column(
            "blocked_for_review",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_repairs_blocked_for_review", "repairs", ["blocked_for_review"]
    )

    op.create_table(
        "repair_status_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "repair_id",
            sa.Integer(),
            sa.ForeignKey("repairs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("from_status", repair_status, nullable=True),
        sa.Column("to_status", repair_status, nullable=False),
        sa.Column(
            "actor_id",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("note", sa.String(500), nullable=True),
    )
    op.create_index(
        "ix_repair_status_history_repair_id",
        "repair_status_history",
        ["repair_id"],
    )
    op.create_index(
        "ix_repair_status_history_actor_id", "repair_status_history", ["actor_id"]
    )
    op.create_index(
        "ix_repair_status_history_created_at",
        "repair_status_history",
        ["created_at"],
    )
    op.execute("ALTER TABLE public.repair_status_history ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_repair_status_history_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'repair status history is append-only';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER repair_status_history_append_only
        BEFORE UPDATE OR DELETE ON repair_status_history
        FOR EACH ROW
        EXECUTE FUNCTION prevent_repair_status_history_mutation()
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                REVOKE ALL PRIVILEGES ON TABLE repair_status_history FROM anon;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                REVOKE ALL PRIVILEGES ON TABLE repair_status_history FROM authenticated;
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS repair_status_history_append_only "
        "ON repair_status_history"
    )
    op.execute("DROP FUNCTION IF EXISTS prevent_repair_status_history_mutation()")
    op.drop_table("repair_status_history")

    op.drop_index("ix_repairs_blocked_for_review", table_name="repairs")
    op.drop_column("repairs", "blocked_for_review")
    op.drop_column("repairs", "delivered_at")
    op.drop_index("ix_repairs_sale_id", table_name="repairs")
    op.drop_constraint("uq_repairs_sale_id", "repairs", type_="unique")
    op.drop_constraint("fk_repairs_sale_id", "repairs", type_="foreignkey")
    op.drop_column("repairs", "sale_id")
    op.drop_index("ix_repairs_branch_id", table_name="repairs")
    op.drop_constraint("fk_repairs_branch_id", "repairs", type_="foreignkey")
    op.drop_column("repairs", "branch_id")

    op.drop_constraint("ck_repairs_folio_prefix", "repairs", type_="check")
    op.drop_constraint("ck_repairs_price_nonnegative", "repairs", type_="check")
    op.execute("ALTER TABLE repairs RENAME COLUMN price TO quoted_price")
    op.create_check_constraint(
        "ck_repairs_quoted_price_nonnegative",
        "repairs",
        "quoted_price IS NULL OR quoted_price >= 0",
    )

    op.alter_column("repairs", "status", server_default=None)
    op.execute("ALTER TABLE repairs ALTER COLUMN status TYPE VARCHAR USING status::text")
    op.execute(
        """
        UPDATE repairs
        SET status = CASE status
            WHEN 'received' THEN 'recibido'
            WHEN 'ready' THEN 'terminado'
            ELSE 'en_proceso'
        END
        """
    )
    op.execute("DROP TYPE repair_status")
    legacy_status = postgresql.ENUM(
        "recibido",
        "pendiente_taller",
        "en_proceso",
        "terminado",
        "enviado",
        name="repair_status",
        create_type=False,
    )
    legacy_status.create(op.get_bind(), checkfirst=True)
    op.execute(
        "ALTER TABLE repairs ALTER COLUMN status TYPE repair_status "
        "USING status::repair_status"
    )
