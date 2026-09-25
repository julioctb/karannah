from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RepairStatus(str, enum.Enum):
    RECIBIDO = "recibido"
    PENDIENTE_TALLER = "pendiente_taller"
    EN_PROCESO = "en_proceso"
    TERMINADO = "terminado"
    ENVIADO = "enviado"


class Repair(Base):
    __tablename__ = "repairs"
    __table_args__ = (
        CheckConstraint(
            "quoted_price IS NULL OR quoted_price >= 0",
            name="ck_repairs_quoted_price_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    folio: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    client_name: Mapped[str] = mapped_column(String(200))  # texto libre si no es cliente registrado
    product_description: Mapped[str] = mapped_column(String(255))
    service: Mapped[str] = mapped_column(String(160))
    status: Mapped[RepairStatus] = mapped_column(
        Enum(RepairStatus, name="repair_status", values_callable=lambda r: [e.value for e in r]),
        default=RepairStatus.RECIBIDO,
        index=True,
    )
    quoted_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    received_at: Mapped[date] = mapped_column(Date)
    expected_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
