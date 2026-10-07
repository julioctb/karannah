from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ensure_role, get_current_profile
from app.core.db import get_db
from app.models.identity import Role, UserProfile
from app.models.settings import CompanySettings
from app.schemas.settings import CompanySettingsRead, CompanySettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


async def _get_or_create_company_settings(db: AsyncSession) -> CompanySettings:
    settings = await db.get(CompanySettings, 1)
    if settings is not None:
        return settings

    settings = CompanySettings(id=1)
    db.add(settings)
    try:
        await db.flush()
        return settings
    except IntegrityError:
        # Otra solicitud pudo crear el singleton entre la lectura y el insert.
        await db.rollback()
        existing = await db.get(CompanySettings, 1)
        if existing is None:  # pragma: no cover - protege una invariante de base de datos
            raise
        return existing


@router.get("/company", response_model=CompanySettingsRead)
async def get_company_settings(db: Db, profile: Profile) -> CompanySettings:
    del profile  # La lectura está disponible para cualquier perfil autenticado.
    settings = await _get_or_create_company_settings(db)
    await db.commit()
    await db.refresh(settings)
    return settings


@router.patch("/company", response_model=CompanySettingsRead)
async def update_company_settings(
    payload: CompanySettingsUpdate,
    db: Db,
    profile: Profile,
) -> CompanySettings:
    ensure_role(profile, Role.ADMIN)
    settings = await _get_or_create_company_settings(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return settings
