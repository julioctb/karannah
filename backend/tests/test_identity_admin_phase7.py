from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_claims, get_current_profile
from app.core.db import Base, get_db
from app.core.security import TokenClaims
from app.main import app
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile

ADMIN_ID = uuid.uuid4()
OTHER_ADMIN_ID = uuid.uuid4()
VENDOR_ID = uuid.uuid4()
T01_ID = uuid.uuid4()
T02_ID = uuid.uuid4()
INACTIVE_BRANCH_ID = uuid.uuid4()


@pytest_asyncio.fixture()
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add_all(
            [
                Branch(id=T01_ID, code="T01", name="Centro"),
                Branch(id=T02_ID, code="T02", name="Norte"),
                Branch(
                    id=INACTIVE_BRANCH_ID,
                    code="T99",
                    name="Cerrada",
                    active=False,
                ),
                UserProfile(
                    id=ADMIN_ID,
                    email="admin@joyeria.local",
                    full_name="Admin Principal",
                    role=Role.ADMIN,
                ),
                UserProfile(
                    id=OTHER_ADMIN_ID,
                    email="admin2@joyeria.local",
                    full_name="Admin Secundaria",
                    role=Role.ADMIN,
                ),
                UserProfile(
                    id=VENDOR_ID,
                    email="venta@joyeria.local",
                    full_name="Venta Centro",
                    role=Role.VENDEDOR,
                ),
            ]
        )
        await session.flush()
        session.add(UserBranchAssignment(user_id=VENDOR_ID, branch_id=T01_ID))
        await session.commit()
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture()
async def client(session_factory):
    async def override_db():
        async with session_factory() as session:
            yield session

    def as_admin():
        return TokenClaims(
            user_id=str(ADMIN_ID), email="admin@joyeria.local", role="admin"
        )

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_claims] = as_admin
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as api_client:
        yield api_client
    app.dependency_overrides.clear()


async def test_admin_lists_existing_profiles_with_assignments(client):
    response = await client.get("/api/v1/users")

    assert response.status_code == 200
    users = {row["email"]: row for row in response.json()}
    assert set(users) == {
        "admin@joyeria.local",
        "admin2@joyeria.local",
        "venta@joyeria.local",
    }
    assert users["admin@joyeria.local"]["branches"] == []
    assert users["venta@joyeria.local"]["branches"] == [
        {"id": str(T01_ID), "code": "T01", "name": "Centro", "active": True}
    ]


async def test_non_admin_cannot_list_or_update_profiles(client):
    def as_vendor():
        return TokenClaims(
            user_id=str(VENDOR_ID), email="venta@joyeria.local", role="vendedor"
        )

    app.dependency_overrides[get_current_claims] = as_vendor
    list_response = await client.get("/api/v1/users")
    update_response = await client.patch(
        f"/api/v1/users/{OTHER_ADMIN_ID}",
        json={
            "full_name": "Cambio",
            "role": "admin",
            "active": True,
            "branch_ids": [],
        },
    )

    assert list_response.status_code == 403
    assert update_response.status_code == 403


async def test_admin_updates_profile_and_replaces_all_assignments(client, session_factory):
    response = await client.patch(
        f"/api/v1/users/{VENDOR_ID}",
        json={
            "full_name": "  Encargada Norte  ",
            "role": "encargado",
            "active": True,
            "branch_ids": [str(T02_ID)],
        },
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Encargada Norte"
    assert response.json()["role"] == "encargado"
    assert [branch["id"] for branch in response.json()["branches"]] == [str(T02_ID)]
    async with session_factory() as session:
        assigned = set(
            await session.scalars(
                select(UserBranchAssignment.branch_id).where(
                    UserBranchAssignment.user_id == VENDOR_ID
                )
            )
        )
    assert assigned == {T02_ID}


async def test_admin_cannot_edit_own_profile(client):
    response = await client.patch(
        f"/api/v1/users/{ADMIN_ID}",
        json={
            "full_name": "Admin Principal",
            "role": "admin",
            "active": True,
            "branch_ids": [],
        },
    )

    assert response.status_code == 409


async def test_update_rejects_unknown_user(client):
    response = await client.patch(
        f"/api/v1/users/{uuid.uuid4()}",
        json={
            "full_name": "Nadie",
            "role": "vendedor",
            "active": True,
            "branch_ids": [str(T01_ID)],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"


async def test_non_admin_requires_at_least_one_active_branch(client):
    response = await client.patch(
        f"/api/v1/users/{VENDOR_ID}",
        json={
            "full_name": "Venta Centro",
            "role": "vendedor",
            "active": True,
            "branch_ids": [],
        },
    )

    assert response.status_code == 422


async def test_update_rejects_missing_or_inactive_branch(client):
    payload = {
        "full_name": "Venta Centro",
        "role": "vendedor",
        "active": True,
        "branch_ids": [str(uuid.uuid4())],
    }
    missing = await client.patch(f"/api/v1/users/{VENDOR_ID}", json=payload)
    payload["branch_ids"] = [str(INACTIVE_BRANCH_ID)]
    inactive = await client.patch(f"/api/v1/users/{VENDOR_ID}", json=payload)

    assert missing.status_code == 404
    assert missing.json()["detail"] == "Sucursal no encontrada"
    assert inactive.status_code == 404
    assert inactive.json()["detail"] == "Sucursal no encontrada"


async def test_admin_role_clears_assignments(client, session_factory):
    response = await client.patch(
        f"/api/v1/users/{VENDOR_ID}",
        json={
            "full_name": "Nueva Admin",
            "role": "admin",
            "active": True,
            "branch_ids": [],
        },
    )

    assert response.status_code == 200
    assert response.json()["branches"] == []
    async with session_factory() as session:
        assigned = list(
            await session.scalars(
                select(UserBranchAssignment.id).where(
                    UserBranchAssignment.user_id == VENDOR_ID
                )
            )
        )
    assert assigned == []


async def test_admin_role_rejects_branch_assignments(client):
    response = await client.patch(
        f"/api/v1/users/{VENDOR_ID}",
        json={
            "full_name": "Nueva Admin",
            "role": "admin",
            "active": True,
            "branch_ids": [str(T01_ID)],
        },
    )

    assert response.status_code == 422


async def test_last_active_admin_cannot_be_deactivated(client, session_factory):
    async with session_factory() as session:
        actor = await session.get(UserProfile, ADMIN_ID)
        assert actor is not None
        actor.active = False
        await session.commit()

    async def inactive_admin_actor():
        return UserProfile(
            id=ADMIN_ID,
            email="admin@joyeria.local",
            full_name="Admin Principal",
            role=Role.ADMIN,
            active=False,
        )

    app.dependency_overrides[get_current_profile] = inactive_admin_actor
    response = await client.patch(
        f"/api/v1/users/{OTHER_ADMIN_ID}",
        json={
            "full_name": "Admin Secundaria",
            "role": "vendedor",
            "active": True,
            "branch_ids": [str(T01_ID)],
        },
    )

    assert response.status_code == 409
