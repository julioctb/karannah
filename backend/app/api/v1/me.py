from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_profile, visible_branches
from app.core.db import get_db
from app.models.identity import UserProfile
from app.schemas.auth import BranchesResponse, BranchRead, MeResponse

router = APIRouter(tags=["auth"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


@router.get("/me", response_model=MeResponse)
async def me(db: Db, profile: Profile) -> MeResponse:
    branches = await visible_branches(db, profile)
    return MeResponse(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        role=profile.role.value,
        branches=[BranchRead.model_validate(b) for b in branches],
    )


@router.get("/me/branches", response_model=BranchesResponse)
async def my_branches(db: Db, profile: Profile) -> BranchesResponse:
    branches = await visible_branches(db, profile)
    return BranchesResponse(branches=[BranchRead.model_validate(b) for b in branches])
