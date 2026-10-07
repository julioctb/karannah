from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ensure_role, get_current_profile
from app.auth_admin import AuthAdminLifecycle, get_auth_admin_lifecycle
from app.core.db import get_db
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile
from app.schemas.auth import BranchRead, UserAdminRead, UserAdminUpdate

router = APIRouter(prefix="/users", tags=["users"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]
Lifecycle = Annotated[AuthAdminLifecycle, Depends(get_auth_admin_lifecycle)]


async def _profile_branches(db: AsyncSession, user_id: uuid.UUID) -> list[Branch]:
    return list(
        await db.scalars(
            select(Branch)
            .join(UserBranchAssignment, UserBranchAssignment.branch_id == Branch.id)
            .where(UserBranchAssignment.user_id == user_id)
            .order_by(Branch.code)
        )
    )


async def _read_profile(db: AsyncSession, profile: UserProfile) -> UserAdminRead:
    branches = [] if profile.role is Role.ADMIN else await _profile_branches(db, profile.id)
    return UserAdminRead(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        role=profile.role.value,
        active=profile.active,
        branches=[BranchRead.model_validate(branch) for branch in branches],
    )


@router.get("", response_model=list[UserAdminRead])
async def list_users(db: Db, profile: Profile) -> list[UserAdminRead]:
    ensure_role(profile, Role.ADMIN)
    rows = list(await db.scalars(select(UserProfile).order_by(UserProfile.full_name, UserProfile.email)))
    return [await _read_profile(db, row) for row in rows]


@router.patch("/{user_id}", response_model=UserAdminRead)
async def update_user(
    user_id: uuid.UUID,
    payload: UserAdminUpdate,
    db: Db,
    profile: Profile,
    lifecycle: Lifecycle,
) -> UserAdminRead:
    ensure_role(profile, Role.ADMIN)
    target = await db.scalar(
        select(UserProfile).where(UserProfile.id == user_id).with_for_update()
    )
    if target is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if target.id == profile.id:
        raise HTTPException(status_code=409, detail="No puedes modificar tu propia cuenta")

    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=422, detail="El nombre completo es obligatorio")
    role = Role(payload.role)
    branch_ids = list(dict.fromkeys(payload.branch_ids))
    if role is Role.ADMIN and branch_ids:
        raise HTTPException(status_code=422, detail="Los administradores no tienen asignaciones")
    if role is not Role.ADMIN and not branch_ids:
        raise HTTPException(
            status_code=422,
            detail="El usuario debe tener al menos una sucursal activa",
        )

    branches: list[Branch] = []
    if branch_ids:
        branches = list(
            await db.scalars(
                select(Branch)
                .where(Branch.id.in_(branch_ids), Branch.active.is_(True))
                .order_by(Branch.code)
            )
        )
        if {branch.id for branch in branches} != set(branch_ids):
            raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    removes_active_admin = (
        target.role is Role.ADMIN
        and target.active
        and (role is not Role.ADMIN or not payload.active)
    )
    if removes_active_admin:
        active_admin_ids = list(
            await db.scalars(
                select(UserProfile.id)
                .where(UserProfile.role == Role.ADMIN, UserProfile.active.is_(True))
                .order_by(UserProfile.id)
                .with_for_update()
            )
        )
        if len(active_admin_ids) <= 1:
            raise HTTPException(
                status_code=409,
                detail="Debe conservarse al menos un administrador activo",
            )

    await lifecycle.sync_active_state(
        db,
        target,
        active=payload.active,
        actor_id=profile.id,
    )
    target.full_name = full_name
    target.role = role
    target.active = payload.active
    await db.execute(
        delete(UserBranchAssignment).where(UserBranchAssignment.user_id == target.id)
    )
    for branch in branches:
        db.add(UserBranchAssignment(user_id=target.id, branch_id=branch.id))
    await db.commit()
    return await _read_profile(db, target)
