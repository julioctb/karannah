from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ClientType(str, enum.Enum):
    MENUDEO = "menudeo"
    MAYOREO = "mayoreo"


class CreditMovementType(str, enum.Enum):
    VENTA_CREDITO = "venta_credito"
    ABONO = "abono"
    AJUSTE = "ajuste"


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        CheckConstraint(
            "credit_limit IS NULL OR credit_limit >= 0",
            name="ck_clients_credit_limit_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    type: Mapped[ClientType] = mapped_column(
        Enum(ClientType, name="client_type", values_callable=lambda r: [e.value for e in r])
    )
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CreditEntry(Base):
    """Ledger inmutable de crédito. Saldo del cliente = SUM(quantity).

    quantity positivo = deuda adquirida; negativo = abono. Nunca se
    actualiza ni se borra; las correcciones son entradas nuevas.
    """

    __tablename__ = "credit_entries"
    __table_args__ = (CheckConstraint("quantity <> 0", name="ck_credit_entries_quantity_nonzero"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), index=True
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # +deuda / -abono
    movement_type: Mapped[CreditMovementType] = mapped_column(
        Enum(
            CreditMovementType,
            name="credit_movement_type",
            values_callable=lambda r: [e.value for e in r],
        )
    )
    reference: Mapped[str | None] = mapped_column(String(60), nullable=True)  # folio de venta
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sale_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cash_session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cash_sessions.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
