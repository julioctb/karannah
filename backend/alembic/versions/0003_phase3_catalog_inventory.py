"""Phase 3 catalog variants, SKU counters and variant inventory.

Revision ID: 0003_phase3
Revises: 0002_domain
Create Date: 2026-09-18
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_phase3"
down_revision: str | None = "0002_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "categories", sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False)
    )
    op.add_column(
        "materials", sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False)
    )
    op.add_column("products", sa.Column("variant_type", sa.String(length=40), nullable=True))
    op.add_column(
        "products", sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False)
    )

    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sku", sa.String(length=32), nullable=False),
        sa.Column("variant_value", sa.String(length=80), nullable=True),
        sa.Column("cost_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("retail_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("wholesale_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.CheckConstraint("cost_price >= 0", name="ck_product_variants_cost_nonnegative"),
        sa.CheckConstraint("retail_price >= 0", name="ck_product_variants_retail_nonnegative"),
        sa.CheckConstraint(
            "wholesale_price >= 0", name="ck_product_variants_wholesale_nonnegative"
        ),
        sa.UniqueConstraint("product_id", "variant_value", name="uq_product_variant_value"),
    )
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])
    op.create_index("ix_product_variants_sku", "product_variants", ["sku"], unique=True)
    op.execute(
        """
        INSERT INTO product_variants
            (id, product_id, sku, variant_value, cost_price, retail_price, wholesale_price, active)
        SELECT id, id, sku, NULL, cost_price, retail_price, wholesale_price, true
        FROM products
        """
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('product_variants', 'id'),
            COALESCE((SELECT MAX(id) FROM product_variants), 1),
            EXISTS (SELECT 1 FROM product_variants)
        )
        """
    )

    op.add_column("stock_entries", sa.Column("variant_id", sa.Integer(), nullable=True))
    op.add_column("sale_items", sa.Column("variant_id", sa.Integer(), nullable=True))
    op.execute("UPDATE stock_entries SET variant_id = product_id")
    op.execute("UPDATE sale_items SET variant_id = product_id")
    op.alter_column("stock_entries", "variant_id", nullable=False)
    op.alter_column("sale_items", "variant_id", nullable=False)
    op.create_foreign_key(
        "fk_stock_entries_variant",
        "stock_entries",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_sale_items_variant", "sale_items", "product_variants", ["variant_id"], ["id"]
    )
    op.create_index("ix_stock_entries_variant_id", "stock_entries", ["variant_id"])
    op.create_index("ix_sale_items_variant_id", "sale_items", ["variant_id"])
    op.drop_constraint("stock_entries_product_id_fkey", "stock_entries", type_="foreignkey")
    op.drop_constraint("sale_items_product_id_fkey", "sale_items", type_="foreignkey")
    op.drop_index("ix_stock_entries_product_id", table_name="stock_entries")
    op.drop_index("ix_sale_items_product_id", table_name="sale_items")
    op.drop_column("stock_entries", "product_id")
    op.drop_column("sale_items", "product_id")

    op.create_table(
        "sku_counters",
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("next_value", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("next_value >= 1", name="ck_sku_counters_positive"),
    )
    op.execute(
        """
        INSERT INTO sku_counters (category_id, next_value)
        SELECT c.id, COALESCE(MAX((substring(v.sku from '([0-9]+)$'))::integer), 0) + 1
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        LEFT JOIN product_variants v ON v.product_id = p.id
        GROUP BY c.id
        """
    )

    op.drop_index("ix_products_sku", table_name="products")
    op.drop_constraint("ck_products_cost_price_nonnegative", "products", type_="check")
    op.drop_constraint("ck_products_retail_price_nonnegative", "products", type_="check")
    op.drop_constraint("ck_products_wholesale_price_nonnegative", "products", type_="check")
    op.drop_column("products", "sku")
    op.drop_column("products", "cost_price")
    op.drop_column("products", "retail_price")
    op.drop_column("products", "wholesale_price")

    for table in ("product_variants", "sku_counters"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                REVOKE ALL PRIVILEGES ON TABLE product_variants, sku_counters FROM anon;
                REVOKE ALL PRIVILEGES ON SEQUENCE product_variants_id_seq FROM anon;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                REVOKE ALL PRIVILEGES ON TABLE product_variants, sku_counters FROM authenticated;
                REVOKE ALL PRIVILEGES ON SEQUENCE product_variants_id_seq FROM authenticated;
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM products p
                LEFT JOIN product_variants v ON v.product_id = p.id
                GROUP BY p.id HAVING count(v.id) <> 1
            ) THEN
                RAISE EXCEPTION 'No se puede revertir: existen productos sin una variante unica';
            END IF;
        END $$
        """
    )
    op.add_column("products", sa.Column("sku", sa.String(length=32), nullable=True))
    op.add_column("products", sa.Column("cost_price", sa.Numeric(12, 2), nullable=True))
    op.add_column("products", sa.Column("retail_price", sa.Numeric(12, 2), nullable=True))
    op.add_column("products", sa.Column("wholesale_price", sa.Numeric(12, 2), nullable=True))
    op.execute(
        """
        UPDATE products p SET
            sku = v.sku,
            cost_price = v.cost_price,
            retail_price = v.retail_price,
            wholesale_price = v.wholesale_price
        FROM product_variants v WHERE v.product_id = p.id
        """
    )
    for column in ("sku", "cost_price", "retail_price", "wholesale_price"):
        op.alter_column("products", column, nullable=False)
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_check_constraint("ck_products_cost_price_nonnegative", "products", "cost_price >= 0")
    op.create_check_constraint(
        "ck_products_retail_price_nonnegative", "products", "retail_price >= 0"
    )
    op.create_check_constraint(
        "ck_products_wholesale_price_nonnegative", "products", "wholesale_price >= 0"
    )

    op.add_column("stock_entries", sa.Column("product_id", sa.Integer(), nullable=True))
    op.add_column("sale_items", sa.Column("product_id", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE stock_entries s SET product_id = v.product_id FROM product_variants v WHERE v.id = s.variant_id"
    )
    op.execute(
        "UPDATE sale_items s SET product_id = v.product_id FROM product_variants v WHERE v.id = s.variant_id"
    )
    op.alter_column("stock_entries", "product_id", nullable=False)
    op.alter_column("sale_items", "product_id", nullable=False)
    op.create_foreign_key(
        "stock_entries_product_id_fkey",
        "stock_entries",
        "products",
        ["product_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "sale_items_product_id_fkey", "sale_items", "products", ["product_id"], ["id"]
    )
    op.create_index("ix_stock_entries_product_id", "stock_entries", ["product_id"])
    op.create_index("ix_sale_items_product_id", "sale_items", ["product_id"])
    op.drop_constraint("fk_stock_entries_variant", "stock_entries", type_="foreignkey")
    op.drop_constraint("fk_sale_items_variant", "sale_items", type_="foreignkey")
    op.drop_index("ix_stock_entries_variant_id", table_name="stock_entries")
    op.drop_index("ix_sale_items_variant_id", table_name="sale_items")
    op.drop_column("stock_entries", "variant_id")
    op.drop_column("sale_items", "variant_id")
    op.drop_table("sku_counters")
    op.drop_table("product_variants")
    op.drop_column("products", "active")
    op.drop_column("products", "variant_type")
    op.drop_column("materials", "active")
    op.drop_column("categories", "active")
