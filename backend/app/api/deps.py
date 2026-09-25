from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import AuthError, TokenClaims, decode_access_token
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_claims(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenClaims:
    """Extrae y valida las claims del JWT de Supabase del header Authorization."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Falta el token de autenticación")
    try:
        return await decode_access_token(credentials.credentials)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=exc.message) from exc


async def load_profile(db: AsyncSession, user_id: str) -> UserProfile:
    """Perfil activo del usuario; 401/403 si el token no mapea a uno válido."""
    try:
        uid = uuid.UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Identificador de usuario inválido") from exc

    profile = await db.get(UserProfile, uid)
    if profile is None or not profile.active:
        raise HTTPException(status_code=403, detail="Usuario sin perfil activo")
    return profile


async def get_current_profile(
    claims: TokenClaims = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    return await load_profile(db, claims.user_id)


async def visible_branches(db: AsyncSession, profile: UserProfile) -> list[Branch]:
    """Única fuente de verdad del alcance de sucursales.

    admin ve todas las activas; el resto solo las asignadas.
    """
    stmt = select(Branch).where(Branch.active.is_(True)).order_by(Branch.code)
    if profile.role != Role.ADMIN:
        stmt = stmt.join(UserBranchAssignment, UserBranchAssignment.branch_id == Branch.id).where(
            UserBranchAssignment.user_id == profile.id
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def visible_branch_ids(db: AsyncSession, profile: UserProfile) -> list[uuid.UUID]:
    return [b.id for b in await visible_branches(db, profile)]


def ensure_role(profile: UserProfile, *roles: Role) -> None:
    """Autoriza una accion usando exclusivamente el rol canonico del perfil."""
    if profile.role not in roles:
        raise HTTPException(status_code=403, detail="Accion no autorizada para este rol")


async def require_visible_branch(
    db: AsyncSession, profile: UserProfile, branch_id: uuid.UUID
) -> Branch:
    branch = await db.get(Branch, branch_id)
    if branch is None or not branch.active:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    if profile.role != Role.ADMIN:
        assignment = await db.scalar(
            select(UserBranchAssignment.id).where(
                UserBranchAssignment.user_id == profile.id,
                UserBranchAssignment.branch_id == branch_id,
            )
        )
        if assignment is None:
            raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return branch
