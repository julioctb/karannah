from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.sales import PaymentMethod, SaleCondition, SaleStatus, SaleType


class QuoteItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant_id: int
    quantity: int = Field(gt=0)


class QuoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: uuid.UUID
    sale_type: SaleType = SaleType.MENUDEO
    items: list[QuoteItemCreate] = Field(min_length=1, max_length=100)
    discount_percent: Decimal = Field(default=Decimal(0), ge=0, le=100, decimal_places=2)
    promotion_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def variants_must_be_unique(self) -> QuoteCreate:
        variant_ids = [item.variant_id for item in self.items]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError("Cada variante debe aparecer una sola vez")
        return self


class QuoteLineRead(BaseModel):
    variant_id: int
    sku: str
    product_name: str
    variant_value: str | None
    quantity: int
    available_quantity: int
    unit_price: Decimal
    base: Decimal
    discount: Decimal
    subtotal: Decimal
    tax: Decimal
    total: Decimal


class QuoteRead(BaseModel):
    branch_id: uuid.UUID
    sale_type: SaleType
    lines: list[QuoteLineRead]
    base: Decimal
    discount_percent: Decimal
    discount: Decimal
    promotion_id: int | None = None
    promotion_name: str | None = None
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    approval_required: bool
    fingerprint: str


class CheckoutPaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: PaymentMethod
    amount: Decimal = Field(gt=0, decimal_places=2)

    @model_validator(mode="after")
    def method_must_be_payable(self) -> CheckoutPaymentCreate:
        if self.method is PaymentMethod.MIXTO:
            raise ValueError("mixto no es un metodo de pago individual")
        return self


class CheckoutCreate(QuoteCreate):
    client_id: int | None = None
    cash_session_id: uuid.UUID
    payments: list[CheckoutPaymentCreate] = Field(max_length=10)
    discount_approval_id: uuid.UUID | None = None


class PaymentRead(BaseModel):
    id: uuid.UUID
    method: PaymentMethod
    amount: Decimal
    cash_session_id: uuid.UUID | None
    created_at: datetime


class SaleItemRead(BaseModel):
    id: int
    variant_id: int | None
    sku: str
    product_name: str
    variant_value: str | None
    quantity: int
    unit_price: Decimal
    base: Decimal
    discount: Decimal
    subtotal: Decimal
    tax: Decimal
    total: Decimal


class SaleRead(BaseModel):
    id: int
    folio: str
    branch_id: uuid.UUID
    branch_code: str
    client_id: int | None = None
    client_name: str | None = None
    seller_name: str | None = None
    sale_type: SaleType
    condition: SaleCondition
    status: SaleStatus
    payment_method: PaymentMethod
    subtotal: Decimal = Decimal(0)
    discount: Decimal = Decimal(0)
    discount_percent: Decimal = Decimal(0)
    tax: Decimal = Decimal(0)
    total: Decimal
    discount_approved_by: uuid.UUID | None = None
    promotion_id: int | None = None
    promotion_name: str | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    created_at: datetime


class SaleDetailRead(SaleRead):
    items: list[SaleItemRead]
    payments: list[PaymentRead]


class DiscountApprovalCreate(QuoteCreate):
    expires_in_minutes: int = Field(default=10, ge=1, le=60)


class DiscountApprovalRead(BaseModel):
    id: uuid.UUID
    branch_id: uuid.UUID
    request_fingerprint: str
    max_discount_percent: Decimal
    approved_by: uuid.UUID
    created_at: datetime
    expires_at: datetime
    consumed_at: datetime | None = None


class CancelSaleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=3, max_length=255)
