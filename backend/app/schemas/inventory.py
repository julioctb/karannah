from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.inventory import StockMovementType


class StockLevel(BaseModel):
    variant_id: int
    product_id: int
    sku: str
    product_name: str
    variant_value: str | None = None
    branch_id: uuid.UUID
    branch_code: str
    branch_name: str
    quantity: int


class InventoryAdjustmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant_id: int
    branch_id: uuid.UUID
    quantity: int
    reference: str | None = Field(default=None, max_length=60)
    note: str = Field(min_length=1, max_length=255)

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_nonzero(cls, value: int) -> int:
        if value == 0:
            raise ValueError("La cantidad no puede ser cero")
        return value


class InventoryMovementRead(BaseModel):
    id: uuid.UUID
    variant_id: int
    branch_id: uuid.UUID
    quantity: int
    movement_type: StockMovementType
    reference: str | None
    note: str | None
    created_by: uuid.UUID | None
    created_at: datetime


class InventoryAdjustmentRead(InventoryMovementRead):
    resulting_quantity: int
