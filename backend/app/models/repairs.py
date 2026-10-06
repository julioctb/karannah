from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    event,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class RepairStatus(str, enum.Enum):
    RECEIVED = "received"
    IN_WORKSHOP = "in_workshop"
    READY = "ready"


_REPAIR_STATUS_TYPE = Enum(
    RepairStatus,
    name="repair_status",
    values_callable=lambda enum_type: [item.value for item in enum_type],
)


class Repair(Base):
    __tablename__ = "repairs"
    __table_args__ = (
        CheckConstraint(
            "folio LIKE 'RP-%' OR folio LIKE 'R-%'",
            name="ck_repairs_folio_prefix",
        ),
        CheckConstraint(
            "price IS NULL OR price >= 0",
            name="ck_repairs_price_nonnegative",
        ),
        UniqueConstraint("sale_id", name="uq_repairs_sale_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    folio: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    # Legacy rows predate branch ownership. F6-02 will require this value for every
    # new intake while list visibility remains global.
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    client_name: Mapped[str] = mapped_column(String(200))
    product_description: Mapped[str] = mapped_column(String(255))
    service: Mapped[str] = mapped_column(String(160))
    status: Mapped[RepairStatus] = mapped_column(
        _REPAIR_STATUS_TYPE,
        default=RepairStatus.RECEIVED,
        server_default=RepairStatus.RECEIVED.value,
        index=True,
    )
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    received_at: Mapped[date] = mapped_column(Date)
    expected_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sale_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    blocked_for_review: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False, index=True
    )

    history: Mapped[list[RepairStatusHistory]] = relationship(
        back_populates="repair", order_by="RepairStatusHistory.created_at"
    )


class RepairStatusHistory(Base):
    __tablename__ = "repair_status_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    repair_id: Mapped[int] = mapped_column(
        ForeignKey("repairs.id", ondelete="RESTRICT"), index=True
    )
    from_status: Mapped[RepairStatus | None] = mapped_column(
        _REPAIR_STATUS_TYPE, nullable=True
    )
    to_status: Mapped[RepairStatus] = mapped_column(_REPAIR_STATUS_TYPE)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    repair: Mapped[Repair] = relationship(back_populates="history")


@event.listens_for(RepairStatusHistory, "before_update")
@event.listens_for(RepairStatusHistory, "before_delete")
def _prevent_history_mutation(*_args: object) -> None:
    """Keep history append-only when writes pass through the ORM."""
    raise ValueError("repair status history is append-only")
