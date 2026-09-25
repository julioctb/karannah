from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_claims
from app.core.db import Base, get_db
from app.core.security import TokenClaims
from app.main import app
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile

ADMIN_ID = uuid.uuid4()
VENDEDOR_ID = uuid.uuid4()


@pytest_asyncio.fixture()
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        t01 = Branch(id=uuid.uuid4(), code="T01", name="Sucursal Centro")
        t02 = Branch(id=uuid.uuid4(), code="T02", name="Sucursal Norte")
        a01 = Branch(id=uuid.uuid4(), code="A01", name="Almacén")
        admin = UserProfile(
            id=ADMIN_ID, email="admin@joyeria.com", full_name="Admin", role=Role.ADMIN
        )
        vendedor = UserProfile(
            id=VENDEDOR_ID,
            email="vendedor@joyeria.com",
            full_name="Vendedora T01",
            role=Role.VENDEDOR,
        )
        inactivo = UserProfile(
            id=uuid.uuid4(),
            email="baja@joyeria.com",
            full_name="Baja",
            role=Role.VENDEDOR,
            active=False,
        )
        s.add_all([t01, t02, a01, admin, vendedor, inactivo])
        await s.flush()
        s.add(UserBranchAssignment(user_id=VENDEDOR_ID, branch_id=t01.id))
        await s.commit()
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture()
async def client(session_factory):
    async def override_db():
        async with session_factory() as s:
            yield s

    def as_admin():
        return TokenClaims(user_id=str(ADMIN_ID), email="admin@joyeria.com", role="admin")

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_claims] = as_admin
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_me_admin(client):
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"
    assert data["email"] == "admin@joyeria.com"
    assert sorted(b["code"] for b in data["branches"]) == ["A01", "T01", "T02"]


async def test_me_branches_vendedor_limited(client, session_factory):
    def as_vendedor():
        return TokenClaims(user_id=str(VENDEDOR_ID), email="vendedor@joyeria.com", role="vendedor")

    app.dependency_overrides[get_current_claims] = as_vendedor
    resp = await client.get("/api/v1/me/branches")
    assert resp.status_code == 200
    codes = [b["code"] for b in resp.json()["branches"]]
    assert codes == ["T01"]


async def test_me_user_without_profile_403(client):
    def as_unknown():
        return TokenClaims(user_id=str(uuid.uuid4()), email="x@x.com", role=None)

    app.dependency_overrides[get_current_claims] = as_unknown
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 403


async def test_me_inactive_user_403(client, session_factory):
    # perfil inactivo: usamos el id creado en el fixture buscándolo por email
    async with session_factory() as s:
        from sqlalchemy import select

        from app.models.identity import UserProfile as UP

        row = (await s.execute(select(UP).where(UP.email == "baja@joyeria.com"))).scalar_one()
        uid = str(row.id)

    def as_inactive():
        return TokenClaims(user_id=uid, email="baja@joyeria.com", role="vendedor")

    app.dependency_overrides[get_current_claims] = as_inactive
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 403


async def test_me_invalid_uuid_401(client):
    def as_junk():
        return TokenClaims(user_id="no-soy-uuid", email="x@x.com", role=None)

    app.dependency_overrides[get_current_claims] = as_junk
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 401
