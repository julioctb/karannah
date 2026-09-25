from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    ensure_role,
    get_current_profile,
    require_visible_branch,
    visible_branch_ids,
)
from app.api.pagination import PaginationParams
from app.core.config import get_settings
from app.core.db import get_db
from app.models.clients import Client
from app.models.identity import Branch, Role, UserProfile
from app.models.sales import DiscountApproval, Sale
from app.schemas.sales import (
    CancelSaleCreate,
    CheckoutCreate,
    DiscountApprovalCreate,
    DiscountApprovalRead,
    QuoteCreate,
    QuoteRead,
    SaleDetailRead,
    SaleRead,
)
from app.services.pos import DISCOUNT_LIMITS, build_quote, cancel_sale, checkout, sale_detail

router = APIRouter(prefix="/sales", tags=["sales"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


def _day_bounds(d: date) -> tuple[datetime, datetime]:
    timezone = ZoneInfo(get_settings().business_timezone)
    start = datetime.combine(d, time.min, tzinfo=timezone)
    return start, start + timedelta(days=1)


@router.get("", response_model=list[SaleRead])
async def list_sales(
    db: Db,
    profile: Profile,
    page: PaginationParams,
    branch_id: Annotated[uuid.UUID | None, Query()] = None,
    client_id: Annotated[int | None, Query()] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> list[SaleRead]:
    """Ventas restringidas a las sucursales visibles del usuario."""
    limit, offset = page
    branch_ids = await visible_branch_ids(db, profile)
    if branch_id is not None:
        if branch_id not in branch_ids:
            return []
        branch_ids = [branch_id]
    if not branch_ids:
        return []

    stmt = (
        select(
            Sale.id,
            Sale.folio,
            Sale.branch_id,
            Branch.code.label("branch_code"),
            Sale.client_id,
            Client.name.label("client_name"),
            UserProfile.full_name.label("seller_name"),
            Sale.sale_type,
            Sale.condition,
            Sale.status,
            Sale.payment_method,
            Sale.subtotal,
            Sale.discount,
            Sale.discount_percent,
            Sale.tax,
            Sale.total,
            Sale.discount_approved_by,
            Sale.cancelled_at,
            Sale.cancellation_reason,
            Sale.created_at,
        )
        .join(Branch, Branch.id == Sale.branch_id)
        .outerjoin(Client, Client.id == Sale.client_id)
        .outerjoin(UserProfile, UserProfile.id == Sale.user_id)
        .where(Sale.branch_id.in_(branch_ids))
        .order_by(Sale.created_at.desc(), Sale.id.desc())
    )
    if client_id is not None:
        stmt = stmt.where(Sale.client_id == client_id)
    if date_from is not None:
        start, _ = _day_bounds(date_from)
        stmt = stmt.where(Sale.created_at >= start)
    if date_to is not None:
        _, next_day = _day_bounds(date_to)
        stmt = stmt.where(Sale.created_at < next_day)

    result = await db.execute(stmt.limit(limit).offset(offset))
    return [SaleRead.model_validate(dict(row)) for row in result.mappings().all()]


@router.post("/quote", response_model=QuoteRead)
async def quote_sale(payload: QuoteCreate, db: Db, profile: Profile) -> QuoteRead:
    await require_visible_branch(db, profile, payload.branch_id)
    return await build_quote(db, payload, profile)


@router.post(
    "/discount-approvals",
    response_model=DiscountApprovalRead,
    status_code=status.HTTP_201_CREATED,
)
async def approve_discount(
    payload: DiscountApprovalCreate, db: Db, profile: Profile
) -> DiscountApproval:
    ensure_role(profile, Role.ADMIN, Role.ENCARGADO)
    await require_visible_branch(db, profile, payload.branch_id)
    if payload.discount_percent > DISCOUNT_LIMITS[profile.role]:
        raise HTTPException(status_code=403, detail="El descuento excede el limite del aprobador")
    quote = await build_quote(db, payload, profile)
    approval = DiscountApproval(
        branch_id=payload.branch_id,
        request_fingerprint=quote.fingerprint,
        max_discount_percent=payload.discount_percent,
        approved_by=profile.id,
        expires_at=datetime.now(UTC) + timedelta(minutes=payload.expires_in_minutes),
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval


@router.post("/checkout", response_model=SaleDetailRead, status_code=status.HTTP_201_CREATED)
async def checkout_sale(
    payload: CheckoutCreate,
    db: Db,
    profile: Profile,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=120)],
) -> SaleDetailRead:
    branch = await require_visible_branch(db, profile, payload.branch_id)
    key = idempotency_key.strip()
    if not key:
        raise HTTPException(status_code=422, detail="Idempotency-Key no puede estar vacio")
    result = await checkout(db, payload, profile, branch, key)
    await db.commit()
    return result


@router.get("/{sale_id}", response_model=SaleDetailRead)
async def get_sale(sale_id: int, db: Db, profile: Profile) -> SaleDetailRead:
    sale = await db.get(Sale, sale_id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    await require_visible_branch(db, profile, sale.branch_id)
    return await sale_detail(db, sale_id)


@router.post("/{sale_id}/cancel", response_model=SaleDetailRead)
async def cancel_sale_route(
    sale_id: int,
    payload: CancelSaleCreate,
    db: Db,
    profile: Profile,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=120)],
) -> SaleDetailRead:
    ensure_role(profile, Role.ADMIN, Role.ENCARGADO)
    sale = await db.get(Sale, sale_id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    await require_visible_branch(db, profile, sale.branch_id)
    key = idempotency_key.strip()
    if not key:
        raise HTTPException(status_code=422, detail="Idempotency-Key no puede estar vacio")
    result = await cancel_sale(db, sale_id, payload, profile, key)
    await db.commit()
    return result
