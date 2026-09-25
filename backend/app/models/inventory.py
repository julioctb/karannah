from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class StockMovementType(str, enum.Enum):
    INICIAL = "inicial"
    VENTA = "venta"
    DEVOLUCION = "devolucion"
    AJUSTE = "ajuste"
    CONTEO = "conteo"
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"
    TRANSFERENCIA_SALIDA = "transferencia_salida"


class StockTransferStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    RECEIVED = "received"


class PhysicalCountStatus(str, enum.Enum):
    OPEN = "open"
    FINALIZED = "finalized"


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


class StockTransfer(Base):
    __tablename__ = "stock_transfers"
    __table_args__ = (
        CheckConstraint("folio LIKE 'TR-%'", name="ck_stock_transfers_folio_prefix"),
        CheckConstraint(
            "origin_branch_id <> destination_branch_id",
            name="ck_stock_transfers_distinct_branches",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    folio: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    origin_branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    destination_branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[StockTransferStatus] = mapped_column(
        Enum(
            StockTransferStatus,
            name="stock_transfer_status",
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        default=StockTransferStatus.DRAFT,
        server_default=StockTransferStatus.DRAFT.value,
        index=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sent_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True
    )
    received_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lines: Mapped[list[StockTransferLine]] = relationship(
        back_populates="transfer", cascade="all, delete-orphan"
    )


class StockTransferLine(Base):
    __tablename__ = "stock_transfer_lines"
    __table_args__ = (
        CheckConstraint(
            "shipped_quantity > 0",
            name="ck_stock_transfer_lines_shipped_quantity_positive",
        ),
        CheckConstraint(
            "received_quantity IS NULL OR received_quantity >= 0",
            name="ck_stock_transfer_lines_received_quantity_nonnegative",
        ),
        CheckConstraint(
            "shortage_quantity IS NULL OR shortage_quantity >= 0",
            name="ck_stock_transfer_lines_shortage_quantity_nonnegative",
        ),
        CheckConstraint(
            "received_quantity IS NULL OR received_quantity <= shipped_quantity",
            name="ck_stock_transfer_lines_received_not_over_shipped",
        ),
        CheckConstraint(
            "(received_quantity IS NULL AND shortage_quantity IS NULL) OR "
            "(received_quantity IS NOT NULL AND shortage_quantity IS NOT NULL AND "
            "shortage_quantity = shipped_quantity - received_quantity)",
            name="ck_stock_transfer_lines_shortage_matches_received",
        ),
        UniqueConstraint("transfer_id", "variant_id", name="uq_stock_transfer_line_variant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transfer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stock_transfers.id", ondelete="CASCADE"), index=True
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), index=True
    )
    shipped_quantity: Mapped[int] = mapped_column(Integer)
    received_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shortage_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    transfer: Mapped[StockTransfer] = relationship(back_populates="lines")


class PhysicalCount(Base):
    __tablename__ = "physical_counts"
    __table_args__ = (
        CheckConstraint("folio LIKE 'CF-%'", name="ck_physical_counts_folio_prefix"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    folio: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[PhysicalCountStatus] = mapped_column(
        Enum(
            PhysicalCountStatus,
            name="physical_count_status",
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        default=PhysicalCountStatus.OPEN,
        server_default=PhysicalCountStatus.OPEN.value,
        index=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    finalized_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lines: Mapped[list[PhysicalCountLine]] = relationship(
        back_populates="count", cascade="all, delete-orphan"
    )


class PhysicalCountLine(Base):
    __tablename__ = "physical_count_lines"
    __table_args__ = (
        CheckConstraint(
            "snapshot_quantity >= 0",
            name="ck_physical_count_lines_snapshot_quantity_nonnegative",
        ),
        CheckConstraint(
            "observed_quantity IS NULL OR observed_quantity >= 0",
            name="ck_physical_count_lines_observed_quantity_nonnegative",
        ),
        UniqueConstraint(
            "physical_count_id",
            "variant_id",
            name="uq_physical_count_lines_physical_count_variant",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    physical_count_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("physical_counts.id", ondelete="CASCADE"), index=True
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), index=True
    )
    snapshot_quantity: Mapped[int] = mapped_column(Integer)
    observed_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    count: Mapped[PhysicalCount] = relationship(back_populates="lines")
