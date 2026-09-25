from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.clients import ClientType, CreditMovementType
from app.models.sales import PaymentMethod


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: ClientType
    phone: str | None = None
    email: str | None = None
    credit_limit: Decimal | None = None
    notes: str | None = None
    active: bool = True
    created_at: datetime
    credit_balance: Decimal


class ClientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=500)


class ClientUpdate(ClientCreate):
    name: str | None = Field(default=None, min_length=1, max_length=200)


class ClientCommercialUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ClientType
    credit_limit: Decimal | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def retail_has_no_credit(self) -> ClientCommercialUpdate:
        if self.type is ClientType.MENUDEO and self.credit_limit is not None:
            raise ValueError("Un cliente de menudeo no puede tener limite de credito")
        return self


class CreditPaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: uuid.UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    method: PaymentMethod
    cash_session_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def validate_method_and_session(self) -> CreditPaymentCreate:
        allowed = {
            PaymentMethod.EFECTIVO,
            PaymentMethod.TARJETA,
            PaymentMethod.TRANSFERENCIA,
        }
        if self.method not in allowed:
            raise ValueError("Metodo no permitido para un abono")
        if self.method is PaymentMethod.EFECTIVO and self.cash_session_id is None:
            raise ValueError("El abono en efectivo requiere una sesion de caja")
        if self.method is not PaymentMethod.EFECTIVO and self.cash_session_id is not None:
            raise ValueError("Solo los abonos en efectivo usan sesion de caja")
        return self


class CreditPaymentRead(BaseModel):
    id: uuid.UUID
    client_id: int
    amount: Decimal
    method: PaymentMethod
    cash_session_id: uuid.UUID | None
    resulting_balance: Decimal
    created_at: datetime


class CreditLedgerRead(BaseModel):
    id: uuid.UUID
    client_id: int
    branch_id: uuid.UUID | None
    branch_code: str | None = None
    quantity: Decimal
    movement_type: CreditMovementType
    reference: str | None
    note: str | None
    sale_id: int | None
    payment_method: str | None
    cash_session_id: uuid.UUID | None
    created_by: uuid.UUID | None
    created_at: datetime
