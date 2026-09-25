from __future__ import annotations

import uuid

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app import provision_user
from app.core.config import Settings
from app.core.db import Base
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile
from app.provision_user import provision_profile


@pytest.fixture()
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as db:
        db.add_all(
            [
                Branch(code="T01", name="Tienda Centro"),
                Branch(code="T02", name="Tienda Norte"),
            ]
        )
        await db.commit()
        yield db
    await engine.dispose()


async def test_provision_vendor_assigns_requested_branches(session: AsyncSession) -> None:
    user_id = uuid.uuid4()
    profile = await provision_profile(
        session,
        user_id=user_id,
        email="VENDEDOR@EXAMPLE.COM",
        full_name="Vendedor Uno",
        role=Role.VENDEDOR,
        branch_codes=["t01"],
    )
    await session.commit()

    assert profile.email == "vendedor@example.com"
    assignments = await session.scalar(
        select(func.count())
        .select_from(UserBranchAssignment)
        .where(UserBranchAssignment.user_id == user_id)
    )
    assert assignments == 1


async def test_changing_to_admin_removes_assignments(session: AsyncSession) -> None:
    user_id = uuid.uuid4()
    await provision_profile(
        session,
        user_id=user_id,
        email="admin@example.com",
        full_name="Admin",
        role=Role.VENDEDOR,
        branch_codes=["T01"],
    )
    await provision_profile(
        session,
        user_id=user_id,
        email="admin@example.com",
        full_name="Admin",
        role=Role.ADMIN,
        branch_codes=[],
    )
    await session.commit()

    assignments = await session.scalar(
        select(func.count())
        .select_from(UserBranchAssignment)
        .where(UserBranchAssignment.user_id == user_id)
    )
    assert assignments == 0
    assert (await session.get(UserProfile, user_id)).role is Role.ADMIN


async def test_non_admin_requires_branch(session: AsyncSession) -> None:
    with pytest.raises(ValueError, match="requieren al menos una sucursal"):
        await provision_profile(
            session,
            user_id=uuid.uuid4(),
            email="seller@example.com",
            full_name="Seller",
            role=Role.VENDEDOR,
            branch_codes=[],
        )


async def test_invite_auth_user_uses_supabase_admin_api(monkeypatch) -> None:
    user_id = uuid.uuid4()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/auth/v1/invite"
        assert request.headers["apikey"] == "service-secret"
        assert request.headers["authorization"] == "Bearer service-secret"
        return httpx.Response(200, json={"id": str(user_id)})

    original_client = httpx.AsyncClient
    client = original_client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(
        provision_user,
        "get_settings",
        lambda: Settings(
            supabase_url="https://example.supabase.co",
            supabase_service_role_key="service-secret",
        ),
    )
    monkeypatch.setattr(provision_user.httpx, "AsyncClient", lambda **_: client)

    invited_id = await provision_user.invite_auth_user(
        "user@example.com", "Usuario", "https://app.example.com"
    )
    assert invited_id == user_id
