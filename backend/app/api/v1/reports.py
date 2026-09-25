from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ensure_role, get_current_profile, visible_branch_ids
from app.api.pagination import PaginationParams
from app.core.config import get_settings
from app.core.db import get_db
from app.models.clients import Client, CreditEntry, CreditMovementType
from app.models.identity import Role, UserProfile
from app.schemas.reports import CreditRecoveryReportRead, CreditRecoveryReportRow

router = APIRouter(prefix="/reports", tags=["reports"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    timezone = ZoneInfo(get_settings().business_timezone)
    start = datetime.combine(day, time.min, tzinfo=timezone)
    return start, start + timedelta(days=1)


def _movement_scope(
    branch_ids: list[uuid.UUID], branch_id: uuid.UUID | None
):
    if branch_id is not None:
        return CreditEntry.branch_id == branch_id
    return or_(CreditEntry.branch_id.in_(branch_ids), CreditEntry.branch_id.is_(None))


@router.get("/credit-recovery", response_model=CreditRecoveryReportRead)
async def credit_recovery_report(
    db: Db,
    profile: Profile,
    page: PaginationParams,
    branch_id: Annotated[uuid.UUID | None, Query()] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> CreditRecoveryReportRead:
    ensure_role(profile, Role.ADMIN, Role.ENCARGADO)
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from no puede ser posterior a date_to")

    branch_ids = await visible_branch_ids(db, profile)
    if branch_id is not None and branch_id not in branch_ids:
        return CreditRecoveryReportRead(
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            total_clients=0,
            totals={
                "clients_with_balance": 0,
                "current_balance": Decimal(0),
                "period_charged": Decimal(0),
                "period_recovered": Decimal(0),
                "period_net": Decimal(0),
            },
            rows=[],
        )
    if not branch_ids:
        return CreditRecoveryReportRead(
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            total_clients=0,
            totals={
                "clients_with_balance": 0,
                "current_balance": Decimal(0),
                "period_charged": Decimal(0),
                "period_recovered": Decimal(0),
                "period_net": Decimal(0),
            },
            rows=[],
        )

    limit, offset = page
    scope = _movement_scope(branch_ids, branch_id)
    balance = (
        select(
            CreditEntry.client_id.label("client_id"),
            func.coalesce(func.sum(CreditEntry.quantity), 0).label("current_balance"),
        )
        .where(scope)
        .group_by(CreditEntry.client_id)
        .subquery()
    )
    period_scope = [scope]
    if date_from is not None:
        start, _ = _day_bounds(date_from)
        period_scope.append(CreditEntry.created_at >= start)
    if date_to is not None:
        _, next_day = _day_bounds(date_to)
        period_scope.append(CreditEntry.created_at < next_day)
    period = (
        select(
            CreditEntry.client_id.label("client_id"),
            func.coalesce(
                func.sum(
                    case(
                        (CreditEntry.movement_type == CreditMovementType.VENTA_CREDITO, CreditEntry.quantity),
                        else_=0,
                    )
                ),
                0,
            ).label("period_charged"),
            func.coalesce(
                func.sum(
                    case(
                        (CreditEntry.movement_type == CreditMovementType.ABONO, -CreditEntry.quantity),
                        else_=0,
                    )
                ),
                0,
            ).label("period_recovered"),
            func.max(
                case(
                    (CreditEntry.movement_type == CreditMovementType.ABONO, CreditEntry.created_at),
                    else_=None,
                )
            ).label("last_payment_at"),
        )
        .where(*period_scope)
        .group_by(CreditEntry.client_id)
        .subquery()
    )
    report = (
        select(
            Client.id.label("client_id"),
            Client.name.label("client_name"),
            Client.phone,
            Client.email,
            Client.credit_limit,
            balance.c.current_balance,
            func.coalesce(period.c.period_charged, 0).label("period_charged"),
            func.coalesce(period.c.period_recovered, 0).label("period_recovered"),
            period.c.last_payment_at,
        )
        .join(balance, balance.c.client_id == Client.id)
        .outerjoin(period, period.c.client_id == Client.id)
        .where(balance.c.current_balance > 0)
        .order_by(balance.c.current_balance.desc(), Client.name, Client.id)
    ).subquery()

    total_row = (
        await db.execute(
            select(
                func.count(report.c.client_id).label("total_clients"),
                func.coalesce(func.sum(report.c.current_balance), 0).label("current_balance"),
                func.coalesce(func.sum(report.c.period_charged), 0).label("period_charged"),
                func.coalesce(func.sum(report.c.period_recovered), 0).label("period_recovered"),
            )
        )
    ).one()
    rows = (
        await db.execute(
            select(report).limit(limit).offset(offset)
        )
    ).mappings().all()

    def decimal(value: Decimal | int | None) -> Decimal:
        return Decimal(value or 0)

    total_clients = int(total_row.total_clients or 0)
    current_balance = decimal(total_row.current_balance)
    period_charged = decimal(total_row.period_charged)
    period_recovered = decimal(total_row.period_recovered)
    return CreditRecoveryReportRead(
        branch_id=branch_id,
        date_from=date_from,
        date_to=date_to,
        total_clients=total_clients,
        totals={
            "clients_with_balance": total_clients,
            "current_balance": current_balance,
            "period_charged": period_charged,
            "period_recovered": period_recovered,
            "period_net": period_charged - period_recovered,
        },
        rows=[
            CreditRecoveryReportRow(
                **dict(row),
                period_net=decimal(row["period_charged"]) - decimal(row["period_recovered"]),
            )
            for row in rows
        ],
    )
