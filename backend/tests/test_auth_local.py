from __future__ import annotations

import time
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import auth_local
from app.api.v1 import auth as auth_routes
from app.core import security
from app.core.config import Settings
from app.core.db import Base, get_db
from app.main import app
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile

TEST_SECRET = "test-local-secret"
TEST_AUDIENCE = "joyeria-local"


def make_settings(**overrides) -> Settings:
    base = {
        "auth_provider": "local",
        "local_jwt_secret": TEST_SECRET,
        "local_jwt_expire_minutes": 60,
        "local_jwt_audience": TEST_AUDIENCE,
        "environment": "development",
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)


@pytest.fixture()
def local_settings(monkeypatch):
    settings = make_settings()
    monkeypatch.setattr(security, "get_settings", lambda: settings)
    monkeypatch.setattr(auth_routes, "get_settings", lambda: settings)
    return settings


# ---------- Unit: find_dev_user ----------


def test_find_dev_user_ok():
    dev_user = auth_local.find_dev_user("admin@joyeria.local", "admin123")
    assert dev_user is not None
    assert dev_user.role == Role.ADMIN


def test_find_dev_user_normaliza_email():
    dev_user = auth_local.find_dev_user("  VENDEDORA@Joyeria.LOCAL ", "vendedora123")
    assert dev_user is not None
    assert dev_user.role == Role.VENDEDOR


def test_find_dev_user_wrong_password():
    assert auth_local.find_dev_user("admin@joyeria.local", "incorrecta") is None


def test_find_dev_user_unknown_email():
    assert auth_local.find_dev_user("nadie@joyeria.local", "admin123") is None


def test_local_user_id_deterministic():
    a = auth_local.local_user_id("Admin@Joyeria.local")
    b = auth_local.local_user_id("admin@joyeria.local")
    assert a == b
    assert isinstance(a, uuid.UUID)


# ---------- Unit: tokens locales ----------


async def test_local_token_roundtrip(local_settings):
    uid = str(uuid.uuid4())
    token, expires_in = security.create_local_token(uid, "admin@joyeria.local", "admin")
    assert expires_in == 3600
    claims = await security.decode_access_token(token)
    assert claims.user_id == uid
    assert claims.email == "admin@joyeria.local"
    assert claims.role == "admin"


async def test_local_token_wrong_secret_rejected(local_settings, monkeypatch):
    uid = str(uuid.uuid4())
    token, _ = security.create_local_token(uid, "x@x.com", "admin")
    other = make_settings(local_jwt_secret="otro-secreto")
    monkeypatch.setattr(security, "get_settings", lambda: other)
    with pytest.raises(security.AuthError):
        await security.decode_access_token(token)


async def test_local_token_wrong_audience_rejected(local_settings):
    forged = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "aud": "otro-publico",
            "exp": int(time.time()) + 60,
        },
        TEST_SECRET,
        algorithm="HS256",
    )
    with pytest.raises(security.AuthError):
        await security.decode_access_token(forged)


async def test_local_token_expired_rejected(local_settings):
    forged = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "aud": TEST_AUDIENCE,
            "exp": int(time.time()) - 10,
        },
        TEST_SECRET,
        algorithm="HS256",
    )
    with pytest.raises(security.AuthError):
        await security.decode_access_token(forged)


# ---------- Integracion: POST /auth/local/login + /me ----------


@pytest_asyncio.fixture()
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        s.add_all(
            [
                Branch(id=uuid.uuid4(), code="T01", name="Sucursal Centro"),
                Branch(id=uuid.uuid4(), code="T02", name="Sucursal Norte"),
                Branch(id=uuid.uuid4(), code="A01", name="Almacen"),
            ]
        )
        await s.commit()
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture()
async def client(session_factory, local_settings):
    async def override_db():
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_db] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_login_admin_y_me_con_token_real(client):
    resp = await client.post(
        "/api/v1/auth/local/login",
        json={"email": "admin@joyeria.local", "password": "admin123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600
    assert data["user"]["role"] == "admin"
    assert sorted(b["code"] for b in data["user"]["branches"]) == ["A01", "T01", "T02"]

    me = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "admin@joyeria.local"


async def test_login_vendedora_ven_las_sucursales_asignadas(client):
    resp = await client.post(
        "/api/v1/auth/local/login",
        json={"email": "vendedora@joyeria.local", "password": "vendedora123"},
    )
    assert resp.status_code == 200
    codes = [b["code"] for b in resp.json()["user"]["branches"]]
    assert codes == ["T01"]


async def test_login_wrong_password_401(client):
    resp = await client.post(
        "/api/v1/auth/local/login",
        json={"email": "admin@joyeria.local", "password": "mala"},
    )
    assert resp.status_code == 401


async def test_login_idempotente_no_duplica_perfles(client, session_factory):
    for _ in range(2):
        resp = await client.post(
            "/api/v1/auth/local/login",
            json={"email": "encargada@joyeria.local", "password": "encargada123"},
        )
        assert resp.status_code == 200
    from sqlalchemy import func, select

    async with session_factory() as s:
        total = (
            await s.execute(
                select(func.count())
                .select_from(UserProfile)
                .where(UserProfile.email == "encargada@joyeria.local")
            )
        ).scalar_one()
    assert total == 1


async def test_sync_local_users_preserves_admin_managed_profile_and_assignments(session_factory):
    from sqlalchemy import select

    async with session_factory() as session:
        t02 = await session.scalar(select(Branch).where(Branch.code == "T02"))
        assert t02 is not None
        profile = UserProfile(
            id=auth_local.local_user_id("vendedora@joyeria.local"),
            email="vendedora@joyeria.local",
            full_name="Nombre Administrado",
            role=Role.ENCARGADO,
            active=False,
        )
        session.add(profile)
        await session.flush()
        session.add(UserBranchAssignment(user_id=profile.id, branch_id=t02.id))
        await session.commit()

        await auth_local.sync_local_users(session)
        await session.commit()
        await session.refresh(profile)
        branch_ids = set(
            await session.scalars(
                select(UserBranchAssignment.branch_id).where(
                    UserBranchAssignment.user_id == profile.id
                )
            )
        )

    assert profile.full_name == "Nombre Administrado"
    assert profile.role == Role.ENCARGADO
    assert profile.active is False
    assert branch_ids == {t02.id}


async def test_login_devuelve_404_fuera_de_local(session_factory, monkeypatch):
    supa = make_settings(auth_provider="supabase")
    monkeypatch.setattr(auth_routes, "get_settings", lambda: supa)

    async def override_db():
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_db] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.post(
            "/api/v1/auth/local/login",
            json={"email": "admin@joyeria.local", "password": "admin123"},
        )
    assert resp.status_code == 404
    app.dependency_overrides.clear()


async def test_me_sin_token_401(client):
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 401
