from __future__ import annotations

import argparse
import asyncio
import uuid

import httpx
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import dispose_engine, get_session_factory
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile


async def invite_auth_user(email: str, full_name: str, redirect_to: str | None = None) -> uuid.UUID:
    """Invita al usuario y devuelve el UUID asignado por Supabase Auth."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Configura SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY")

    headers = {
        "apikey": settings.supabase_service_role_key,
        "authorization": f"Bearer {settings.supabase_service_role_key}",
    }
    params = {"redirect_to": redirect_to} if redirect_to else None
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/invite",
            headers=headers,
            params=params,
            json={"email": email, "data": {"full_name": full_name}},
        )
    if response.is_error:
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        detail = payload.get("msg") or payload.get("message") or response.text
        raise RuntimeError(f"Supabase no pudo invitar al usuario: {detail}")
    try:
        return uuid.UUID(response.json()["id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Supabase devolvio una respuesta de invitacion invalida") from exc


async def provision_profile(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    email: str,
    full_name: str,
    role: Role,
    branch_codes: list[str],
) -> UserProfile:
    """Crea o actualiza el perfil local que corresponde al usuario de Auth."""
    normalized_email = email.strip().lower()
    codes = sorted({code.strip().upper() for code in branch_codes if code.strip()})
    if role is not Role.ADMIN and not codes:
        raise ValueError("Encargados y vendedores requieren al menos una sucursal")

    branches: list[Branch] = []
    if codes:
        result = await session.execute(
            select(Branch).where(Branch.code.in_(codes), Branch.active.is_(True))
        )
        by_code = {branch.code: branch for branch in result.scalars()}
        missing = [code for code in codes if code not in by_code]
        if missing:
            raise ValueError(f"Sucursales inexistentes o inactivas: {', '.join(missing)}")
        branches = [by_code[code] for code in codes]

    profile_by_email = await session.scalar(
        select(UserProfile).where(UserProfile.email == normalized_email)
    )
    if profile_by_email is not None and profile_by_email.id != user_id:
        raise ValueError("El correo ya pertenece a otro usuario")

    profile = await session.get(UserProfile, user_id)
    if profile is None:
        profile = UserProfile(id=user_id, email=normalized_email, full_name=full_name, role=role)
        session.add(profile)
    else:
        profile.email = normalized_email
        profile.full_name = full_name
        profile.role = role
        profile.active = True
    await session.flush()

    await session.execute(
        delete(UserBranchAssignment).where(UserBranchAssignment.user_id == user_id)
    )
    if role is not Role.ADMIN:
        session.add_all(
            UserBranchAssignment(user_id=user_id, branch_id=branch.id) for branch in branches
        )
    await session.flush()
    return profile


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invita y aprovisiona un usuario interno")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", choices=[role.value for role in Role], required=True)
    parser.add_argument("--branch", action="append", default=[])
    parser.add_argument("--redirect-to")
    parser.add_argument(
        "--auth-user-id",
        type=uuid.UUID,
        help="Aprovisiona una identidad ya existente sin enviar otra invitacion",
    )
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    role = Role(args.role)
    factory = get_session_factory()
    try:
        async with factory() as session:
            # Valida sucursales antes de crear la identidad remota.
            if role is not Role.ADMIN:
                codes = sorted({code.strip().upper() for code in args.branch if code.strip()})
                existing = set(
                    await session.scalars(
                        select(Branch.code).where(Branch.code.in_(codes), Branch.active.is_(True))
                    )
                )
                missing = [code for code in codes if code not in existing]
                if not codes or missing:
                    detail = ", ".join(missing) if missing else "ninguna"
                    raise ValueError(f"Sucursales requeridas no disponibles: {detail}")

            normalized_email = args.email.strip().lower()
            existing_profile = await session.scalar(
                select(UserProfile).where(UserProfile.email == normalized_email)
            )
            if existing_profile is not None and args.auth_user_id is None:
                raise ValueError(
                    "El perfil ya existe; usa --auth-user-id para actualizarlo sin invitar"
                )

            user_id = args.auth_user_id or await invite_auth_user(
                normalized_email, args.name, args.redirect_to
            )
            await provision_profile(
                session,
                user_id=user_id,
                email=normalized_email,
                full_name=args.name,
                role=role,
                branch_codes=args.branch,
            )
            await session.commit()
        print(f"Usuario invitado y aprovisionado: {args.email} ({user_id})")
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
