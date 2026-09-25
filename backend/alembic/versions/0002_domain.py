"""Domain: catalog, inventory ledger, clients/credit ledger, sales, repairs

Revision ID: 0002_domain
Revises: 0001_identity
Create Date: 2026-09-13

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_domain"
down_revision: str | None = "0001_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DOMAIN_TABLES = (
    "categories",
    "materials",
    "subcategories",
    "collections",
    "products",
    "product_collections",
    "clients",
    "credit_entries",
    "stock_entries",
    "sales",
    "sale_items",
    "repairs",
)

_DOMAIN_SEQUENCES = (
    "categories_id_seq",
    "materials_id_seq",
    "subcategories_id_seq",
    "collections_id_seq",
    "products_id_seq",
    "product_collections_id_seq",
    "clients_id_seq",
    "sales_id_seq",
    "sale_items_id_seq",
    "repairs_id_seq",
)


def _revoke_direct_api_access() -> None:
    """El backend es privado: anon/authenticated no deben poder leer ni escribir
    estas tablas (ni sus secuencias) por la API REST directa de Supabase."""
    tables = ", ".join(f"public.{table}" for table in _DOMAIN_TABLES)
    sequences = ", ".join(f"'{seq}'" for seq in _DOMAIN_SEQUENCES)
    for role in ("anon", "authenticated"):
        op.execute(
            f"""
            DO $$
            DECLARE seq record;
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                    RETURN;
                END IF;
                REVOKE ALL PRIVILEGES ON TABLE {tables} FROM {role};
                FOR seq IN
                    SELECT c.relname
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = 'public'
                      AND c.relkind = 'S'
                      AND c.relname = ANY (ARRAY[{sequences}])
                LOOP
                    EXECUTE format('REVOKE ALL PRIVILEGES ON SEQUENCE public.%I FROM {role}', seq.relname);
                END LOOP;
            END
            $$
            """
        )


def upgrade() -> None:
    product_group = sa.Enum("joyeria", "nojoyeria", name="product_group")
    product_status = sa.Enum("disponible", "externo", name="product_status")
    stock_movement_type = sa.Enum(
        "inicial",
        "venta",
        "devolucion",
        "ajuste",
        "conteo",
        "transferencia_entrada",
        "transferencia_salida",
        name="stock_movement_type",
    )
    client_type = sa.Enum("menudeo", "mayoreo", name="client_type")
    credit_movement_type = sa.Enum("venta_credito", "abono", "ajuste", name="credit_movement_type")
    sale_type = sa.Enum("menudeo", "mayoreo", name="sale_type")
    sale_condition = sa.Enum("contado", "credito", name="sale_condition")
    payment_method = sa.Enum(
        "efectivo", "tarjeta", "transferencia", "credito", name="payment_method"
    )
    repair_status = sa.Enum(
        "recibido",
        "pendiente_taller",
        "en_proceso",
        "terminado",
        "enviado",
        name="repair_status",
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=4), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("group", product_group, nullable=False),
        sa.Column("requires_material", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(op.f("ix_categories_code"), "categories", ["code"], unique=True)

    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=4), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
    )
    op.create_index(op.f("ix_materials_code"), "materials", ["code"], unique=True)

    op.create_table(
        "subcategories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("category_id", "name", name="uq_subcategory_per_category"),
    )
    op.create_index(op.f("ix_subcategories_category_id"), "subcategories", ["category_id"])

    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("material_id", sa.Integer(), sa.ForeignKey("materials.id"), nullable=True),
        sa.Column(
            "subcategory_id",
            sa.Integer(),
            sa.ForeignKey("subcategories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("stone", sa.String(length=160), nullable=True),
        sa.Column("cost_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("retail_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("wholesale_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", product_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("cost_price >= 0", name="ck_products_cost_price_nonnegative"),
        sa.CheckConstraint("retail_price >= 0", name="ck_products_retail_price_nonnegative"),
        sa.CheckConstraint("wholesale_price >= 0", name="ck_products_wholesale_price_nonnegative"),
    )
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=True)
    op.create_index(op.f("ix_products_category_id"), "products", ["category_id"])
    op.create_index(op.f("ix_products_subcategory_id"), "products", ["subcategory_id"])

    op.create_table(
        "product_collections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "collection_id",
            sa.Integer(),
            sa.ForeignKey("collections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("product_id", "collection_id", name="uq_product_collection"),
    )
    op.create_index(
        op.f("ix_product_collections_product_id"), "product_collections", ["product_id"]
    )
    op.create_index(
        op.f("ix_product_collections_collection_id"),
        "product_collections",
        ["collection_id"],
    )

    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", client_type, nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("credit_limit", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "credit_limit IS NULL OR credit_limit >= 0",
            name="ck_clients_credit_limit_nonnegative",
        ),
    )
    op.create_index(op.f("ix_clients_name"), "clients", ["name"])

    op.create_table(
        "credit_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "client_id",
            sa.Integer(),
            sa.ForeignKey("clients.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("movement_type", credit_movement_type, nullable=False),
        sa.Column("reference", sa.String(length=60), nullable=True),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column(
            "created_by",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("quantity <> 0", name="ck_credit_entries_quantity_nonzero"),
    )
    op.create_index(op.f("ix_credit_entries_client_id"), "credit_entries", ["client_id"])
    op.create_index(op.f("ix_credit_entries_created_at"), "credit_entries", ["created_at"])

    op.create_table(
        "stock_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("movement_type", stock_movement_type, nullable=False),
        sa.Column("reference", sa.String(length=60), nullable=True),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column(
            "created_by",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("quantity <> 0", name="ck_stock_entries_quantity_nonzero"),
    )
    op.create_index(op.f("ix_stock_entries_product_id"), "stock_entries", ["product_id"])
    op.create_index(op.f("ix_stock_entries_branch_id"), "stock_entries", ["branch_id"])
    op.create_index(op.f("ix_stock_entries_created_at"), "stock_entries", ["created_at"])

    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("folio", sa.String(length=30), nullable=False),
        sa.Column("branch_id", sa.Uuid(), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("user_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "client_id",
            sa.Integer(),
            sa.ForeignKey("clients.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sale_type", sale_type, nullable=False),
        sa.Column("condition", sale_condition, nullable=False),
        sa.Column("payment_method", payment_method, nullable=False),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("total >= 0", name="ck_sales_total_nonnegative"),
        sa.CheckConstraint(
            "(condition = 'credito' AND payment_method = 'credito' AND client_id IS NOT NULL) "
            "OR (condition = 'contado' AND payment_method <> 'credito')",
            name="ck_sales_condition_payment",
        ),
    )
    op.create_index(op.f("ix_sales_folio"), "sales", ["folio"], unique=True)
    op.create_index(op.f("ix_sales_branch_id"), "sales", ["branch_id"])
    op.create_index(op.f("ix_sales_user_id"), "sales", ["user_id"])
    op.create_index(op.f("ix_sales_client_id"), "sales", ["client_id"])
    op.create_index(op.f("ix_sales_created_at"), "sales", ["created_at"])

    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sale_id",
            sa.Integer(),
            sa.ForeignKey("sales.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_sale_items_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="ck_sale_items_unit_price_nonnegative"),
    )
    op.create_index(op.f("ix_sale_items_sale_id"), "sale_items", ["sale_id"])
    op.create_index(op.f("ix_sale_items_product_id"), "sale_items", ["product_id"])

    op.create_table(
        "repairs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("folio", sa.String(length=30), nullable=False),
        sa.Column(
            "client_id",
            sa.Integer(),
            sa.ForeignKey("clients.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("client_name", sa.String(length=200), nullable=False),
        sa.Column("product_description", sa.String(length=255), nullable=False),
        sa.Column("service", sa.String(length=160), nullable=False),
        sa.Column("status", repair_status, nullable=False),
        sa.Column("quoted_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("received_at", sa.Date(), nullable=False),
        sa.Column("expected_at", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.Date(), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.CheckConstraint(
            "quoted_price IS NULL OR quoted_price >= 0",
            name="ck_repairs_quoted_price_nonnegative",
        ),
    )
    op.create_index(op.f("ix_repairs_folio"), "repairs", ["folio"], unique=True)
    op.create_index(op.f("ix_repairs_client_id"), "repairs", ["client_id"])
    op.create_index(op.f("ix_repairs_status"), "repairs", ["status"])

    for table in _DOMAIN_TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
    _revoke_direct_api_access()


def downgrade() -> None:
    # RLS y privilegios desaparecen junto con las tablas.
    op.drop_table("repairs")
    op.drop_table("sale_items")
    op.drop_table("sales")
    op.drop_table("stock_entries")
    op.drop_table("credit_entries")
    op.drop_table("clients")
    op.drop_table("product_collections")
    op.drop_table("products")
    op.drop_table("collections")
    op.drop_table("subcategories")
    op.drop_table("materials")
    op.drop_table("categories")
    for enum_type in (
        "repair_status",
        "payment_method",
        "sale_condition",
        "sale_type",
        "credit_movement_type",
        "client_type",
        "stock_movement_type",
        "product_status",
        "product_group",
    ):
        sa.Enum(name=enum_type).drop(op.get_bind(), checkfirst=True)
