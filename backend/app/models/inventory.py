from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class StockMovementType(str, enum.Enum):
    INICIAL = "inicial"
    VENTA = "venta"
    DEVOLUCION = "devolucion"
    AJUSTE = "ajuste"
    CONTEO = "conteo"
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"
    TRANSFERENCIA_SALIDA = "transferencia_salida"


class StockEntry(Base):
    """Ledger inmutable de inventario por sucursal.

    El stock NUNCA se edita directamente: el saldo de una sucursal se
    deriva de SUM(quantity) de sus entradas. Las filas no se actualizan
    ni se borran; una corrección es una entrada nueva (AJUSTE).
    """

    __tablename__ = "stock_entries"
    __table_args__ = (CheckConstraint("quantity <> 0", name="ck_stock_entries_quantity_nonzero"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), index=True
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer)  # firmado: +entrada / -salida
    movement_type: Mapped[StockMovementType] = mapped_column(
        Enum(
            StockMovementType,
            name="stock_movement_type",
            values_callable=lambda r: [e.value for e in r],
        )
    )
    reference: Mapped[str | None] = mapped_column(
        String(60), nullable=True
    )  # folio venta/transferencia/conteo
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class StockBalance(Base):
    """Proyeccion bloqueable; StockEntry continua siendo el ledger autoritativo."""

    __tablename__ = "stock_balances"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_stock_balances_quantity_nonnegative"),
    )

    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), primary_key=True
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
