from __future__ import annotations

import re
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_RFC_PATTERN = re.compile(r"^[A-ZÑ&]{3,4}(\d{6})[A-Z0-9]{3}$")
_EMAIL_PATTERN = re.compile(
    r"^(?!\.)(?!.*\.\.)[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+(?<!\.)@"
    r"(?!-)(?!.*\.\.)(?:[A-Z0-9-]+\.)+[A-Z]{2,63}$",
    re.IGNORECASE,
)
_PHONE_ALLOWED_PATTERN = re.compile(r"^(?:\+52\s*)?(?:\(?\d{2,3}\)?[\s.-]*)?\d{3,4}[\s.-]*\d{4}$")


def _trim(value: Any) -> Any:
    return value.strip() if isinstance(value, str) else value


class CompanySettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_name: str
    rfc: str
    fiscal_address: str
    phone: str
    email: str


class CompanySettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_name: str | None = Field(default=None, min_length=1, max_length=160)
    rfc: str | None = Field(default=None, max_length=13)
    fiscal_address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)

    @field_validator("business_name", "fiscal_address", mode="before")
    @classmethod
    def trim_text(cls, value: Any) -> Any:
        return _trim(value)

    @field_validator("rfc", mode="before")
    @classmethod
    def normalize_rfc(cls, value: Any) -> Any:
        value = _trim(value)
        if not isinstance(value, str) or not value:
            return value
        normalized = value.upper()
        match = _RFC_PATTERN.fullmatch(normalized)
        if match is None:
            raise ValueError("RFC invalido")
        compact_date = match.group(1)
        try:
            date(
                2000 + int(compact_date[:2]),
                int(compact_date[2:4]),
                int(compact_date[4:]),
            )
        except ValueError as exc:
            raise ValueError("RFC invalido") from exc
        return normalized

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: Any) -> Any:
        value = _trim(value)
        if not isinstance(value, str) or not value:
            return value
        if _PHONE_ALLOWED_PATTERN.fullmatch(value) is None:
            raise ValueError("El telefono debe ser de Mexico y usar solo digitos, espacios, guiones o parentesis")
        if value.startswith("+") and not value.startswith("+52"):
            raise ValueError("El telefono debe ser de Mexico")
        digits = re.sub(r"\D", "", value)
        if len(digits) == 12 and digits.startswith("52"):
            digits = digits[2:]
        if len(digits) != 10:
            raise ValueError("El telefono debe tener 10 digitos")
        return digits

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: Any) -> Any:
        value = _trim(value)
        if not isinstance(value, str) or not value:
            return value
        normalized = value.lower()
        if _EMAIL_PATTERN.fullmatch(normalized) is None:
            raise ValueError("Email invalido")
        return normalized

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> CompanySettingsUpdate:
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Los campos de empresa no aceptan null")
        return self
