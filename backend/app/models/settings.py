from __future__ import annotations

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CompanySettings(Base):
    """Perfil global de la única empresa operada por la aplicación."""

    __tablename__ = "company_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_company_settings_singleton"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    business_name: Mapped[str] = mapped_column(
        String(160), default="", server_default="", nullable=False
    )
    rfc: Mapped[str] = mapped_column(String(13), default="", server_default="", nullable=False)
    fiscal_address: Mapped[str] = mapped_column(
        String(500), default="", server_default="", nullable=False
    )
    phone: Mapped[str] = mapped_column(String(10), default="", server_default="", nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), default="", server_default="", nullable=False
    )
