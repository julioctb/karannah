from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ensure_role, get_current_profile
from app.core.db import get_db
from app.models.identity import Role, UserProfile
from app.models.promotions import Promotion
from app.schemas.promotions import PromotionCreate, PromotionRead, PromotionUpdate
from app.services.pos import current_business_date

router = APIRouter(prefix="/promotions", tags=["promotions"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


@router.get("", response_model=list[PromotionRead])
async def list_available_promotions(db: Db, profile: Profile) -> list[Promotion]:
    del profile  # Cualquier perfil operativo autenticado puede consultar promociones vigentes.
    today = current_business_date()
    rows = await db.scalars(
        select(Promotion)
        .where(
            Promotion.active.is_(True),
            (Promotion.starts_on.is_(None) | (Promotion.starts_on <= today)),
            (Promotion.ends_on.is_(None) | (Promotion.ends_on >= today)),
        )
        .order_by(Promotion.name, Promotion.id)
    )
    return list(rows)


@router.post("", response_model=PromotionRead, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    payload: PromotionCreate,
    db: Db,
    profile: Profile,
) -> Promotion:
    ensure_role(profile, Role.ADMIN)
    promotion = Promotion(**payload.model_dump())
    db.add(promotion)
    await db.commit()
    await db.refresh(promotion)
    return promotion


@router.patch("/{promotion_id}", response_model=PromotionRead)
async def update_promotion(
    promotion_id: int,
    payload: PromotionUpdate,
    db: Db,
    profile: Profile,
) -> Promotion:
    ensure_role(profile, Role.ADMIN)
    promotion = await db.get(Promotion, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promocion no encontrada")

    changes = payload.model_dump(exclude_unset=True)
    starts_on = changes.get("starts_on", promotion.starts_on)
    ends_on = changes.get("ends_on", promotion.ends_on)
    if starts_on is not None and ends_on is not None and starts_on > ends_on:
        raise HTTPException(status_code=422, detail="starts_on no puede ser posterior a ends_on")
    for field, value in changes.items():
        setattr(promotion, field, value)
    await db.commit()
    await db.refresh(promotion)
    return promotion
