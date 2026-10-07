from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class SalesSummaryTotals(BaseModel):
    total_sold: Decimal
    operation_count: int
    credit_sale_count: int


class SalesSummaryReportRead(BaseModel):
    branch_id: uuid.UUID | None
    date_from: date | None
    date_to: date | None
    totals: SalesSummaryTotals


class CreditRecoveryReportRow(BaseModel):
    client_id: int
    client_name: str
    phone: str | None = None
    email: str | None = None
    credit_limit: Decimal | None = None
    current_balance: Decimal
    period_charged: Decimal
    period_recovered: Decimal
    period_net: Decimal
    last_payment_at: datetime | None = None


class CreditRecoveryReportTotals(BaseModel):
    clients_with_balance: int
    current_balance: Decimal
    period_charged: Decimal
    period_recovered: Decimal
    period_net: Decimal


class CreditRecoveryReportRead(BaseModel):
    branch_id: uuid.UUID | None
    date_from: date | None
    date_to: date | None
    total_clients: int
    totals: CreditRecoveryReportTotals
    rows: list[CreditRecoveryReportRow]
