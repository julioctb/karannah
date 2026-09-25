from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import visible_branches
from app.auth_local import find_dev_user, sync_local_users
from app.core.config import get_settings
from app.core.db import get_db
from app.core.security import create_local_token
from app.models.identity import UserProfile
from app.schemas.auth import BranchRead, LoginRequest, LoginResponse, MeResponse

router = APIRouter(tags=["auth"])

Db = Annotated[AsyncSession, Depends(get_db)]


@router.post("/auth/local/login", response_model=LoginResponse)
async def local_login(payload: LoginRequest, db: Db) -> LoginResponse:
    """Login con credenciales dev. Solo disponible con AUTH_PROVIDER=local."""
    if get_settings().auth_provider != "local":
        raise HTTPException(status_code=404, detail="Endpoint no disponible")

    dev_user = find_dev_user(payload.email, payload.password)
    if dev_user is None:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    await sync_local_users(db)
    await db.commit()

    profile = (
        await db.execute(select(UserProfile).where(UserProfile.email == dev_user.email))
    ).scalar_one()
    if not profile.active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    branches = await visible_branches(db, profile)
    token, expires_in = create_local_token(
        user_id=str(profile.id),
        email=profile.email,
        role=profile.role.value,
    )
    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=MeResponse(
            id=profile.id,
            email=profile.email,
            full_name=profile.full_name,
            role=profile.role.value,
            branches=[BranchRead.model_validate(b) for b in branches],
        ),
    )
