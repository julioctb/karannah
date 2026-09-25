from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.inventory import StockMovementType, StockTransferStatus


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


class TransferLineCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant_id: int
    shipped_quantity: int = Field(gt=0)


class TransferCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin_branch_id: uuid.UUID
    destination_branch_id: uuid.UUID
    lines: list[TransferLineCreate] = Field(min_length=1)


class TransferSend(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note: str | None = Field(default=None, max_length=255)


class TransferReceiveLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant_id: int
    received_quantity: int = Field(ge=0)


class TransferReceive(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lines: list[TransferReceiveLine] = Field(min_length=1)


class TransferLineRead(BaseModel):
    id: uuid.UUID
    variant_id: int
    shipped_quantity: int
    received_quantity: int | None
    shortage_quantity: int | None


class TransferRead(BaseModel):
    id: uuid.UUID
    folio: str
    origin_branch_id: uuid.UUID
    destination_branch_id: uuid.UUID
    status: StockTransferStatus
    created_by: uuid.UUID | None
    sent_by: uuid.UUID | None
    received_by: uuid.UUID | None
    created_at: datetime
    sent_at: datetime | None
    received_at: datetime | None
    lines: list[TransferLineRead]
