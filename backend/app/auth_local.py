from __future__ import annotations

import hmac
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile

LOCAL_USER_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "joyeria-local:users")


class DevUser:
    def __init__(
        self,
        email: str,
        password: str,
        full_name: str,
        role: Role,
        branch_codes: tuple[str, ...] = (),
    ) -> None:
        self.email = email
        self.password = password
        self.full_name = full_name
        self.role = role
        self.branch_codes = branch_codes


# Usuarios de SOLO desarrollo para AUTH_PROVIDER=local. Las contraseñas van en
# texto plano a proposito: este archivo nunca debe usarse como patron de
# produccion (produccion usa Supabase Auth).
DEV_USERS = (
    DevUser(
        email="admin@joyeria.local",
        password="admin123",
        full_name="Admin Local",
        role=Role.ADMIN,
    ),
    DevUser(
        email="encargada@joyeria.local",
        password="encargada123",
        full_name="Encargada T01",
        role=Role.ENCARGADO,
        branch_codes=("T01",),
    ),
    DevUser(
        email="vendedora@joyeria.local",
        password="vendedora123",
        full_name="Vendedora T01",
        role=Role.VENDEDOR,
        branch_codes=("T01",),
    ),
)


def find_dev_user(email: str, password: str) -> DevUser | None:
    """Busca un usuario dev comparando email y password en tiempo constante."""
    email_norm = email.strip().lower()
    for dev_user in DEV_USERS:
        email_matches = hmac.compare_digest(dev_user.email, email_norm)
        password_matches = hmac.compare_digest(dev_user.password, password)
        if email_matches and password_matches:
            return dev_user
    return None


def local_user_id(email: str) -> uuid.UUID:
    """Id deterministico para un email dev (idempotente entre seeds)."""
    return uuid.uuid5(LOCAL_USER_NAMESPACE, email.strip().lower())


async def sync_local_users(session: AsyncSession) -> int:
    """Crea/actualiza los perfiles de los usuarios dev. Devuelve cuantos toco."""
    touched = 0
    for dev_user in DEV_USERS:
        profile = (
            await session.execute(select(UserProfile).where(UserProfile.email == dev_user.email))
        ).scalar_one_or_none()
        if profile is None:
            profile = UserProfile(
                id=local_user_id(dev_user.email),
                email=dev_user.email,
                full_name=dev_user.full_name,
                role=dev_user.role,
            )
            session.add(profile)
            await session.flush()
        else:
            profile.full_name = dev_user.full_name
            profile.role = dev_user.role

        if not dev_user.branch_codes:
            continue
        branches = (
            (await session.execute(select(Branch).where(Branch.code.in_(dev_user.branch_codes))))
            .scalars()
            .all()
        )
        existing = (
            await session.execute(
                select(UserBranchAssignment.branch_id).where(
                    UserBranchAssignment.user_id == profile.id
                )
            )
        ).scalars()
        assigned = set(existing)
        for branch in branches:
            if branch.id not in assigned:
                session.add(UserBranchAssignment(user_id=profile.id, branch_id=branch.id))
        touched += 1
    return touched
