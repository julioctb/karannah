from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cash import CashSessionStatus


class TerminalRead(BaseModel):
    id: uuid.UUID
    branch_id: uuid.UUID
    branch_code: str
    code: str
    name: str
    active: bool


class CashSessionOpen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    terminal_id: uuid.UUID
    opening_amount: Decimal = Field(ge=0, decimal_places=2)


class CashSessionClose(BaseModel):
    model_config = ConfigDict(extra="forbid")

    counted_cash: Decimal = Field(ge=0, decimal_places=2)


class CashSessionRead(BaseModel):
    id: uuid.UUID
    terminal_id: uuid.UUID
    branch_id: uuid.UUID
    opening_amount: Decimal
    expected_cash: Decimal
    counted_cash: Decimal | None
    variance: Decimal | None
    opened_by: uuid.UUID
    closed_by: uuid.UUID | None
    status: CashSessionStatus
    business_date: date
    opened_at: datetime
    closed_at: datetime | None
