from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CashSessionStatus(str, enum.Enum):
    ABIERTA = "abierta"
    CERRADA = "cerrada"


class CashMovementType(str, enum.Enum):
    VENTA = "venta"
    ABONO_CREDITO = "abono_credito"
    CANCELACION_VENTA = "cancelacion_venta"


class Terminal(Base):
    __tablename__ = "terminals"
    __table_args__ = (UniqueConstraint("branch_id", "code", name="uq_terminal_branch_code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())


class CashSession(Base):
    __tablename__ = "cash_sessions"
    __table_args__ = (
        CheckConstraint("opening_amount >= 0", name="ck_cash_sessions_opening_nonnegative"),
        CheckConstraint(
            "counted_cash IS NULL OR counted_cash >= 0",
            name="ck_cash_sessions_counted_nonnegative",
        ),
        Index(
            "uq_cash_sessions_open_terminal",
            "terminal_id",
            unique=True,
            postgresql_where=text("status = 'abierta'"),
            sqlite_where=text("status = 'abierta'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    terminal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("terminals.id", ondelete="RESTRICT"), index=True
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    opening_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    expected_cash: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    counted_cash: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    variance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    opened_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_profiles.id"))
    closed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id"), nullable=True
    )
    status: Mapped[CashSessionStatus] = mapped_column(
        Enum(
            CashSessionStatus,
            name="cash_session_status",
            values_callable=lambda r: [e.value for e in r],
        ),
        default=CashSessionStatus.ABIERTA,
    )
    business_date: Mapped[date] = mapped_column(index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CashMovement(Base):
    """Ledger inmutable de entradas de efectivo posteriores a la apertura."""

    __tablename__ = "cash_movements"
    __table_args__ = (CheckConstraint("amount <> 0", name="ck_cash_movements_amount_nonzero"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    cash_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cash_sessions.id", ondelete="RESTRICT"), index=True
    )
    movement_type: Mapped[CashMovementType] = mapped_column(
        Enum(
            CashMovementType,
            name="cash_movement_type",
            values_callable=lambda r: [e.value for e in r],
        )
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    reference: Mapped[str] = mapped_column(String(60))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_profiles.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
