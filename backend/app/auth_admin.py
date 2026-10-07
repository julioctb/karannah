from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import UserProfile


class AuthAdminLifecycle(Protocol):
    """Boundary for provider-owned account lifecycle operations.

    Phase 7 uses the local profile's ``active`` gate. A Supabase Auth Admin
    implementation belongs to Phase 9 and can be added behind this boundary.
    """

    async def sync_active_state(
        self,
        session: AsyncSession,
        profile: UserProfile,
        *,
        active: bool,
        actor_id: uuid.UUID,
    ) -> None: ...


class ProfileGateAuthAdmin:
    async def sync_active_state(
        self,
        session: AsyncSession,
        profile: UserProfile,
        *,
        active: bool,
        actor_id: uuid.UUID,
    ) -> None:
        del session, profile, active, actor_id


def get_auth_admin_lifecycle() -> AuthAdminLifecycle:
    return ProfileGateAuthAdmin()
