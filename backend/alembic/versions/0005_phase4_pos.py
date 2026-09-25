"""Phase 4 transactional POS, cash control, payments and projections.

Revision ID: 0005_phase4_pos
Revises: 0004_product_images
Create Date: 2026-09-18
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005_phase4_pos"
down_revision: str | None = "0004_product_images"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE payment_method ADD VALUE IF NOT EXISTS 'mixto'")
    cash_status = postgresql.ENUM(
        "abierta", "cerrada", name="cash_session_status", create_type=False
    )
    cash_movement_type = postgresql.ENUM(
        "venta", "abono_credito", name="cash_movement_type", create_type=False
    )
    cash_status.create(op.get_bind(), checkfirst=True)
    cash_movement_type.create(op.get_bind(), checkfirst=True)
    payment_method = postgresql.ENUM(
        "efectivo",
        "tarjeta",
        "transferencia",
        "credito",
        "mixto",
        name="payment_method",
        create_type=False,
    )

    op.add_column(
        "clients", sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False)
    )
    op.create_table(
        "stock_balances",
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column(
            "variant_id",
            sa.Integer(),
            sa.ForeignKey("product_variants.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column("quantity", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint("quantity >= 0", name="ck_stock_balances_quantity_nonnegative"),
    )
    op.execute(
        """
        INSERT INTO stock_balances (branch_id, variant_id, quantity)
        SELECT branch_id, variant_id, SUM(quantity)
        FROM stock_entries
        GROUP BY branch_id, variant_id
        """
    )

    op.create_table(
        "terminals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.UniqueConstraint("branch_id", "code", name="uq_terminal_branch_code"),
    )
    op.create_index("ix_terminals_branch_id", "terminals", ["branch_id"])
    op.execute(
        """
        INSERT INTO terminals (id, branch_id, code, name, active)
        SELECT md5(id::text || '-pos-terminal')::uuid,
               id, 'POS-01', 'Caja principal ' || code, true
        FROM branches WHERE active = true
        """
    )
    op.create_table(
        "cash_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "terminal_id",
            sa.Uuid(),
            sa.ForeignKey("terminals.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("opening_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("expected_cash", sa.Numeric(12, 2), nullable=True),
        sa.Column("counted_cash", sa.Numeric(12, 2), nullable=True),
        sa.Column("variance", sa.Numeric(12, 2), nullable=True),
        sa.Column("opened_by", sa.Uuid(), sa.ForeignKey("user_profiles.id"), nullable=False),
        sa.Column("closed_by", sa.Uuid(), sa.ForeignKey("user_profiles.id"), nullable=True),
        sa.Column("status", cash_status, nullable=False),
        sa.Column("business_date", sa.Date(), nullable=False),
        sa.Column(
            "opened_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("opening_amount >= 0", name="ck_cash_sessions_opening_nonnegative"),
        sa.CheckConstraint(
            "counted_cash IS NULL OR counted_cash >= 0",
            name="ck_cash_sessions_counted_nonnegative",
        ),
    )
    op.create_index("ix_cash_sessions_terminal_id", "cash_sessions", ["terminal_id"])
    op.create_index("ix_cash_sessions_branch_id", "cash_sessions", ["branch_id"])
    op.create_index("ix_cash_sessions_business_date", "cash_sessions", ["business_date"])
    op.create_index(
        "uq_cash_sessions_open_terminal",
        "cash_sessions",
        ["terminal_id"],
        unique=True,
        postgresql_where=sa.text("status = 'abierta'"),
    )
    op.create_table(
        "cash_movements",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "cash_session_id",
            sa.Uuid(),
            sa.ForeignKey("cash_sessions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("movement_type", cash_movement_type, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("reference", sa.String(60), nullable=False),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("user_profiles.id"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("amount > 0", name="ck_cash_movements_amount_positive"),
    )
    op.create_index("ix_cash_movements_cash_session_id", "cash_movements", ["cash_session_id"])

    op.create_table(
        "folio_counters",
        sa.Column("document_type", sa.String(10), primary_key=True),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
        sa.Column("business_year", sa.Integer(), primary_key=True),
        sa.Column("next_value", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("next_value >= 1", name="ck_folio_counters_positive"),
    )
    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("user_profiles.id"), nullable=False),
        sa.Column("endpoint", sa.String(80), nullable=False),
        sa.Column("key", sa.String(120), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("response", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "endpoint", "key", name="uq_idempotency_scope_key"),
    )
    op.create_index("ix_idempotency_records_user_id", "idempotency_records", ["user_id"])
    op.create_table(
        "discount_approvals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("max_discount_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("approved_by", sa.Uuid(), sa.ForeignKey("user_profiles.id"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "max_discount_percent >= 0 AND max_discount_percent <= 100",
            name="ck_discount_approvals_percent",
        ),
    )
    op.create_index("ix_discount_approvals_branch_id", "discount_approvals", ["branch_id"])
    op.create_index(
        "ix_discount_approvals_request_fingerprint",
        "discount_approvals",
        ["request_fingerprint"],
    )

    op.drop_constraint("ck_sales_condition_payment", "sales", type_="check")
    op.add_column("sales", sa.Column("cash_session_id", sa.Uuid(), nullable=True))
    op.add_column(
        "sales", sa.Column("subtotal", sa.Numeric(12, 2), server_default="0", nullable=False)
    )
    op.add_column(
        "sales", sa.Column("discount", sa.Numeric(12, 2), server_default="0", nullable=False)
    )
    op.add_column(
        "sales", sa.Column("discount_percent", sa.Numeric(5, 2), server_default="0", nullable=False)
    )
    op.add_column("sales", sa.Column("tax", sa.Numeric(12, 2), server_default="0", nullable=False))
    op.add_column("sales", sa.Column("discount_approval_id", sa.Uuid(), nullable=True))
    op.add_column("sales", sa.Column("discount_approved_by", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_sales_cash_session",
        "sales",
        "cash_sessions",
        ["cash_session_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_sales_discount_approval",
        "sales",
        "discount_approvals",
        ["discount_approval_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_sales_discount_approved_by",
        "sales",
        "user_profiles",
        ["discount_approved_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_sales_cash_session_id", "sales", ["cash_session_id"])
    op.create_check_constraint("ck_sales_subtotal_nonnegative", "sales", "subtotal >= 0")
    op.create_check_constraint("ck_sales_discount_nonnegative", "sales", "discount >= 0")
    op.create_check_constraint("ck_sales_tax_nonnegative", "sales", "tax >= 0")
    op.create_check_constraint(
        "ck_sales_credit_client", "sales", "condition <> 'credito' OR client_id IS NOT NULL"
    )
    op.execute(
        "UPDATE sales SET subtotal = round(total / 1.16, 2), tax = total - round(total / 1.16, 2)"
    )

    for name, type_ in (
        ("sku", sa.String(32)),
        ("product_name", sa.String(255)),
        ("variant_value", sa.String(80)),
        ("base", sa.Numeric(12, 2)),
        ("discount", sa.Numeric(12, 2)),
        ("subtotal", sa.Numeric(12, 2)),
        ("tax", sa.Numeric(12, 2)),
        ("total", sa.Numeric(12, 2)),
    ):
        op.add_column("sale_items", sa.Column(name, type_, nullable=True))
    op.execute(
        """
        UPDATE sale_items i SET
            sku = v.sku,
            product_name = p.name,
            variant_value = v.variant_value,
            base = i.unit_price * i.quantity,
            discount = 0,
            subtotal = round((i.unit_price * i.quantity) / 1.16, 2),
            tax = (i.unit_price * i.quantity) - round((i.unit_price * i.quantity) / 1.16, 2),
            total = i.unit_price * i.quantity
        FROM product_variants v JOIN products p ON p.id = v.product_id
        WHERE v.id = i.variant_id
        """
    )
    for name in ("sku", "product_name", "base", "discount", "subtotal", "tax", "total"):
        op.alter_column("sale_items", name, nullable=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("method", payment_method, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "cash_session_id",
            sa.Uuid(),
            sa.ForeignKey("cash_sessions.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )
    op.create_index("ix_payments_sale_id", "payments", ["sale_id"])
    op.create_index("ix_payments_cash_session_id", "payments", ["cash_session_id"])
    op.execute(
        """
        INSERT INTO payments (id, sale_id, method, amount, created_at)
        SELECT md5(id::text || '-payment')::uuid, id, payment_method, total, created_at
        FROM sales WHERE total > 0
        """
    )

    op.add_column("credit_entries", sa.Column("sale_id", sa.Integer(), nullable=True))
    op.add_column("credit_entries", sa.Column("payment_method", sa.String(20), nullable=True))
    op.add_column("credit_entries", sa.Column("cash_session_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_credit_entries_sale",
        "credit_entries",
        "sales",
        ["sale_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_credit_entries_cash_session",
        "credit_entries",
        "cash_sessions",
        ["cash_session_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_credit_entries_sale_id", "credit_entries", ["sale_id"])
    op.create_index("ix_credit_entries_cash_session_id", "credit_entries", ["cash_session_id"])
    op.execute(
        """
        UPDATE credit_entries c SET sale_id = s.id, payment_method = 'credito'
        FROM sales s
        WHERE c.movement_type = 'venta_credito' AND c.reference = s.folio
        """
    )

    for table in (
        "stock_balances",
        "terminals",
        "cash_sessions",
        "cash_movements",
        "folio_counters",
        "idempotency_records",
        "discount_approvals",
        "payments",
    ):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                REVOKE ALL PRIVILEGES ON TABLE stock_balances, terminals, cash_sessions,
                    cash_movements, folio_counters, idempotency_records, discount_approvals,
                    payments FROM anon;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                REVOKE ALL PRIVILEGES ON TABLE stock_balances, terminals, cash_sessions,
                    cash_movements, folio_counters, idempotency_records, discount_approvals,
                    payments FROM authenticated;
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM sales WHERE payment_method = 'mixto') THEN
                RAISE EXCEPTION 'No se puede revertir: existen ventas con pagos mixtos';
            END IF;
        END $$
        """
    )
    op.drop_index("ix_credit_entries_cash_session_id", table_name="credit_entries")
    op.drop_index("ix_credit_entries_sale_id", table_name="credit_entries")
    op.drop_constraint("fk_credit_entries_cash_session", "credit_entries", type_="foreignkey")
    op.drop_constraint("fk_credit_entries_sale", "credit_entries", type_="foreignkey")
    op.drop_column("credit_entries", "cash_session_id")
    op.drop_column("credit_entries", "payment_method")
    op.drop_column("credit_entries", "sale_id")
    op.drop_table("payments")
    for name in (
        "total",
        "tax",
        "subtotal",
        "discount",
        "base",
        "variant_value",
        "product_name",
        "sku",
    ):
        op.drop_column("sale_items", name)
    op.drop_constraint("ck_sales_credit_client", "sales", type_="check")
    op.drop_constraint("ck_sales_tax_nonnegative", "sales", type_="check")
    op.drop_constraint("ck_sales_discount_nonnegative", "sales", type_="check")
    op.drop_constraint("ck_sales_subtotal_nonnegative", "sales", type_="check")
    op.drop_index("ix_sales_cash_session_id", table_name="sales")
    op.drop_constraint("fk_sales_discount_approved_by", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_discount_approval", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_cash_session", "sales", type_="foreignkey")
    for name in (
        "discount_approved_by",
        "discount_approval_id",
        "tax",
        "discount_percent",
        "discount",
        "subtotal",
        "cash_session_id",
    ):
        op.drop_column("sales", name)
    op.create_check_constraint(
        "ck_sales_condition_payment",
        "sales",
        "(condition = 'credito' AND payment_method = 'credito' AND client_id IS NOT NULL) "
        "OR (condition = 'contado' AND payment_method <> 'credito')",
    )
    op.drop_table("discount_approvals")
    op.drop_table("idempotency_records")
    op.drop_table("folio_counters")
    op.drop_table("cash_movements")
    op.drop_table("cash_sessions")
    op.drop_table("terminals")
    op.drop_table("stock_balances")
    op.drop_column("clients", "active")
    cash_movement_type = postgresql.ENUM(name="cash_movement_type")
    cash_status = postgresql.ENUM(name="cash_session_status")
    cash_movement_type.drop(op.get_bind())
    cash_status.drop(op.get_bind())
