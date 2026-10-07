from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SaleType(str, enum.Enum):
    MENUDEO = "menudeo"
    MAYOREO = "mayoreo"


class SaleCondition(str, enum.Enum):
    CONTADO = "contado"
    CREDITO = "credito"


class SaleStatus(str, enum.Enum):
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"


class PaymentMethod(str, enum.Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    CREDITO = "credito"
    MIXTO = "mixto"


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("total >= 0", name="ck_sales_total_nonnegative"),
        CheckConstraint("subtotal >= 0", name="ck_sales_subtotal_nonnegative"),
        CheckConstraint("discount >= 0", name="ck_sales_discount_nonnegative"),
        CheckConstraint("tax >= 0", name="ck_sales_tax_nonnegative"),
        CheckConstraint(
            "condition <> 'credito' OR client_id IS NOT NULL",
            name="ck_sales_credit_client",
        ),
        CheckConstraint(
            "(promotion_id IS NULL AND promotion_name IS NULL) OR "
            "(promotion_id IS NOT NULL AND promotion_name IS NOT NULL)",
            name="ck_sales_promotion_attribution",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    folio: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("branches.id"), index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    cash_session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cash_sessions.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    sale_type: Mapped[SaleType] = mapped_column(
        Enum(SaleType, name="sale_type", values_callable=lambda r: [e.value for e in r])
    )
    condition: Mapped[SaleCondition] = mapped_column(
        Enum(SaleCondition, name="sale_condition", values_callable=lambda r: [e.value for e in r])
    )
    status: Mapped[SaleStatus] = mapped_column(
        Enum(SaleStatus, name="sale_status", values_callable=lambda r: [e.value for e in r]),
        default=SaleStatus.CONFIRMADA,
        server_default=SaleStatus.CONFIRMADA.value,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method", values_callable=lambda r: [e.value for e in r])
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, server_default="0")
    tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_approval_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("discount_approvals.id", ondelete="RESTRICT"), nullable=True
    )
    discount_approved_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True
    )
    promotion_id: Mapped[int | None] = mapped_column(
        ForeignKey("promotions.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    promotion_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True
    )
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sale_items_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_sale_items_unit_price_nonnegative"),
        CheckConstraint(
            "(variant_id IS NOT NULL AND repair_id IS NULL) OR "
            "(variant_id IS NULL AND repair_id IS NOT NULL)",
            name="ck_sale_items_single_line_source",
        ),
        UniqueConstraint("repair_id", name="uq_sale_items_repair_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), index=True)
    variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_variants.id"), nullable=True, index=True
    )
    repair_id: Mapped[int | None] = mapped_column(
        ForeignKey("repairs.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    sku: Mapped[str] = mapped_column(String(32), default="", server_default="")
    product_name: Mapped[str] = mapped_column(String(255), default="", server_default="")
    variant_value: Mapped[str | None] = mapped_column(String(80), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    base: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0")


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount <> 0", name="ck_payments_amount_nonzero"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="RESTRICT"), index=True)
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method", values_callable=lambda r: [e.value for e in r]),
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    cash_session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cash_sessions.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FolioCounter(Base):
    __tablename__ = "folio_counters"
    __table_args__ = (CheckConstraint("next_value >= 1", name="ck_folio_counters_positive"),)

    document_type: Mapped[str] = mapped_column(String(10), primary_key=True)
    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), primary_key=True
    )
    business_year: Mapped[int] = mapped_column(Integer, primary_key=True)
    next_value: Mapped[int] = mapped_column(Integer, default=1, server_default="1")


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("user_id", "endpoint", "key", name="uq_idempotency_scope_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_profiles.id"), index=True)
    endpoint: Mapped[str] = mapped_column(String(80))
    key: Mapped[str] = mapped_column(String(120))
    request_hash: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DiscountApproval(Base):
    __tablename__ = "discount_approvals"
    __table_args__ = (
        CheckConstraint(
            "max_discount_percent >= 0 AND max_discount_percent <= 100",
            name="ck_discount_approvals_percent",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    request_fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    max_discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    approved_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_profiles.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
