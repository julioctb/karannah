from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_profile,
    require_visible_branch,
    visible_branch_ids,
)
from app.api.pagination import PaginationParams
from app.core.db import get_db
from app.models.identity import UserProfile
from app.models.repairs import Repair, RepairStatus
from app.schemas.repairs import RepairCreate, RepairRead, RepairUpdate
from app.services.repairs import create_repair as create_repair_service
from app.services.repairs import update_repair as update_repair_service

router = APIRouter(prefix="/repairs", tags=["repairs"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


@router.get("", response_model=list[RepairRead])
async def list_repairs(
    db: Db,
    _profile: Profile,
    page: PaginationParams,
    status: Annotated[RepairStatus | None, Query()] = None,
) -> list[RepairRead]:
    """Reparaciones: no dependen de sucursal, visibles para todos los roles."""
    limit, offset = page
    stmt = select(Repair).order_by(Repair.received_at.desc(), Repair.id.desc())
    if status is not None:
        stmt = stmt.where(Repair.status == status)
    result = await db.execute(stmt.limit(limit).offset(offset))
    return list(result.scalars().all())


@router.post("", response_model=RepairRead, status_code=status.HTTP_201_CREATED)
async def create_repair(
    payload: RepairCreate,
    db: Db,
    profile: Profile,
    idempotency_key: Annotated[
        str, Header(alias="Idempotency-Key", min_length=1, max_length=120)
    ],
) -> RepairRead:
    branch = await require_visible_branch(db, profile, payload.branch_id)
    key = idempotency_key.strip()
    if not key:
        raise HTTPException(status_code=422, detail="Idempotency-Key no puede estar vacio")
    result = await create_repair_service(db, payload, profile, branch, key)
    await db.commit()
    return result


@router.patch("/{repair_id}", response_model=RepairRead)
async def update_repair(
    repair_id: int,
    payload: RepairUpdate,
    db: Db,
    profile: Profile,
) -> RepairRead:
    branch_ids = await visible_branch_ids(db, profile)
    result = await update_repair_service(db, repair_id, payload, branch_ids)
    await db.commit()
    return result
