from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    ensure_role,
    get_current_profile,
    require_visible_branch,
    visible_branch_ids,
)
from app.api.pagination import PaginationParams
from app.core.db import get_db
from app.models.catalog import Product, ProductVariant
from app.models.identity import Branch, Role, UserProfile
from app.models.inventory import StockBalance, StockEntry, StockMovementType
from app.schemas.inventory import (
    InventoryAdjustmentCreate,
    InventoryAdjustmentRead,
    InventoryMovementRead,
    StockLevel,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


@router.get("/stock", response_model=list[StockLevel])
async def list_stock(
    db: Db,
    profile: Profile,
    page: PaginationParams,
    branch_id: Annotated[uuid.UUID | None, Query()] = None,
    search: Annotated[str | None, Query(max_length=120)] = None,
) -> list[StockLevel]:
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
            StockBalance.variant_id,
            ProductVariant.product_id,
            ProductVariant.sku,
            Product.name.label("product_name"),
            ProductVariant.variant_value,
            StockBalance.branch_id,
            Branch.code.label("branch_code"),
            Branch.name.label("branch_name"),
            StockBalance.quantity,
        )
        .join(ProductVariant, ProductVariant.id == StockBalance.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .join(Branch, Branch.id == StockBalance.branch_id)
        .where(StockBalance.branch_id.in_(branch_ids))
        .order_by(Branch.code, ProductVariant.sku)
    )
    if search:
        like = f"%{search}%"
        stmt = stmt.where(ProductVariant.sku.ilike(like) | Product.name.ilike(like))
    rows = (await db.execute(stmt.limit(limit).offset(offset))).mappings().all()
    return [StockLevel.model_validate(dict(row)) for row in rows]


@router.get("/movements", response_model=list[InventoryMovementRead])
async def list_movements(
    db: Db,
    profile: Profile,
    page: PaginationParams,
    branch_id: Annotated[uuid.UUID | None, Query()] = None,
    variant_id: Annotated[int | None, Query()] = None,
) -> list[StockEntry]:
    limit, offset = page
    branch_ids = await visible_branch_ids(db, profile)
    if branch_id is not None:
        if branch_id not in branch_ids:
            return []
        branch_ids = [branch_id]
    if not branch_ids:
        return []
    stmt = (
        select(StockEntry)
        .where(StockEntry.branch_id.in_(branch_ids))
        .order_by(StockEntry.created_at.desc(), StockEntry.id.desc())
    )
    if variant_id is not None:
        stmt = stmt.where(StockEntry.variant_id == variant_id)
    return list((await db.scalars(stmt.limit(limit).offset(offset))).all())


@router.post(
    "/adjustments",
    response_model=InventoryAdjustmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_adjustment(
    payload: InventoryAdjustmentCreate, db: Db, profile: Profile
) -> InventoryAdjustmentRead:
    ensure_role(profile, Role.ADMIN, Role.ENCARGADO)
    await require_visible_branch(db, profile, payload.branch_id)
    variant = (
        await db.execute(
            select(ProductVariant)
            .where(ProductVariant.id == payload.variant_id, ProductVariant.active.is_(True))
            .with_for_update()
        )
    ).scalar_one_or_none()
    if variant is None:
        raise HTTPException(status_code=404, detail="Variante no encontrada")
    balance = await db.scalar(
        select(StockBalance)
        .where(
            StockBalance.variant_id == variant.id,
            StockBalance.branch_id == payload.branch_id,
        )
        .with_for_update()
    )
    current = balance.quantity if balance else 0
    resulting = current + payload.quantity
    if resulting < 0:
        raise HTTPException(status_code=409, detail="El ajuste produciria inventario negativo")
    movement = StockEntry(
        variant_id=variant.id,
        branch_id=payload.branch_id,
        quantity=payload.quantity,
        movement_type=StockMovementType.AJUSTE,
        reference=payload.reference.strip() if payload.reference else None,
        note=payload.note.strip(),
        created_by=profile.id,
    )
    if balance is None:
        balance = StockBalance(
            variant_id=variant.id,
            branch_id=payload.branch_id,
            quantity=resulting,
        )
        db.add(balance)
    else:
        balance.quantity = resulting
    db.add(movement)
    await db.commit()
    await db.refresh(movement)
    return InventoryAdjustmentRead(
        id=movement.id,
        variant_id=movement.variant_id,
        branch_id=movement.branch_id,
        quantity=movement.quantity,
        movement_type=movement.movement_type,
        reference=movement.reference,
        note=movement.note,
        created_by=movement.created_by,
        created_at=movement.created_at,
        resulting_quantity=resulting,
    )
