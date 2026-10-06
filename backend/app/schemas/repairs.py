from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.repairs import RepairStatus


class RepairRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    client_id: int | None = None
    client_name: str
    product_description: str
    service: str
    status: RepairStatus
    price: Decimal | None = None
    received_at: date
    expected_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None
