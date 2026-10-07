from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.repairs import RepairStatus


class RepairIntakeFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_id: int | None = None
    client_name: str | None = Field(default=None, max_length=200)
    confirm_free_text_client: bool = False
    product_description: str = Field(min_length=1, max_length=255)
    service: str = Field(min_length=1, max_length=160)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    received_at: date
    expected_at: date | None = None
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("client_name", "product_description", "service", "notes", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_intake(self) -> RepairIntakeFields:
        if self.client_id is None and (
            not self.client_name or not self.confirm_free_text_client
        ):
            raise ValueError("Cliente libre requiere nombre y confirmacion explicita")
        if self.expected_at is not None and self.expected_at < self.received_at:
            raise ValueError("expected_at no puede ser anterior a received_at")
        return self


class RepairCreate(RepairIntakeFields):
    branch_id: uuid.UUID


class RepairUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_id: int | None = None
    client_name: str | None = Field(default=None, max_length=200)
    confirm_free_text_client: bool = False
    product_description: str | None = Field(default=None, min_length=1, max_length=255)
    service: str | None = Field(default=None, min_length=1, max_length=160)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    received_at: date | None = None
    expected_at: date | None = None
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("client_name", "product_description", "service", "notes", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value


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
