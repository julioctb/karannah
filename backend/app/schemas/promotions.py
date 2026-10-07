from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PromotionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    discount_percent: Decimal
    starts_on: date | None
    ends_on: date | None
    active: bool
    created_at: datetime
    updated_at: datetime


class PromotionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    discount_percent: Decimal = Field(gt=0, le=100, decimal_places=2)
    starts_on: date | None = None
    ends_on: date | None = None

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_date_range(self) -> PromotionCreate:
        if self.starts_on is not None and self.ends_on is not None and self.starts_on > self.ends_on:
            raise ValueError("starts_on no puede ser posterior a ends_on")
        return self


class PromotionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=160)
    discount_percent: Decimal | None = Field(default=None, gt=0, le=100, decimal_places=2)
    starts_on: date | None = None
    ends_on: date | None = None
    active: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> PromotionUpdate:
        required = {"name", "discount_percent", "active"}
        if any(field in self.model_fields_set and getattr(self, field) is None for field in required):
            raise ValueError("name, discount_percent y active no aceptan null")
        return self
