from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_profile
from app.api.pagination import PaginationParams
from app.core.db import get_db
from app.models.identity import UserProfile
from app.models.repairs import Repair, RepairStatus
from app.schemas.repairs import RepairRead

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
