from __future__ import annotations

import enum
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    false,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ProductGroup(str, enum.Enum):
    JOYERIA = "joyeria"
    NO_JOYERIA = "nojoyeria"


class ProductStatus(str, enum.Enum):
    DISPONIBLE = "disponible"
    EXTERNO = "externo"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(4), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    group: Mapped[ProductGroup] = mapped_column(
        Enum(ProductGroup, name="product_group", values_callable=lambda r: [e.value for e in r])
    )
    requires_material: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(4), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )


class Subcategory(Base):
    __tablename__ = "subcategories"
    __table_args__ = (UniqueConstraint("category_id", "name", name="uq_subcategory_per_category"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    material_id: Mapped[int | None] = mapped_column(ForeignKey("materials.id"), nullable=True)
    subcategory_id: Mapped[int | None] = mapped_column(
        ForeignKey("subcategories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    stone: Mapped[str | None] = mapped_column(String(160), nullable=True)
    variant_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name="product_status", values_callable=lambda r: [e.value for e in r])
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        CheckConstraint("cost_price >= 0", name="ck_product_variants_cost_nonnegative"),
        CheckConstraint("retail_price >= 0", name="ck_product_variants_retail_nonnegative"),
        CheckConstraint("wholesale_price >= 0", name="ck_product_variants_wholesale_nonnegative"),
        UniqueConstraint("product_id", "variant_value", name="uq_product_variant_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    sku: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    variant_value: Mapped[str | None] = mapped_column(String(80), nullable=True)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    retail_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    wholesale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )


class SkuCounter(Base):
    __tablename__ = "sku_counters"
    __table_args__ = (CheckConstraint("next_value >= 1", name="ck_sku_counters_positive"),)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, default=1, server_default="1")


class ProductCollection(Base):
    __tablename__ = "product_collections"
    __table_args__ = (
        UniqueConstraint("product_id", "collection_id", name="uq_product_collection"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), index=True
    )
