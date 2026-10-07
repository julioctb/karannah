from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_claims
from app.core.db import Base, get_db
from app.core.security import TokenClaims
from app.main import app
from app.models.identity import Role, UserProfile
from app.models.settings import CompanySettings

ADMIN_ID = uuid.uuid4()
VENDEDOR_ID = uuid.uuid4()


@pytest_asyncio.fixture()
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        session.add_all(
            [
                UserProfile(
                    id=ADMIN_ID,
                    email="admin@joyeria.com",
                    full_name="Admin",
                    role=Role.ADMIN,
                ),
                UserProfile(
                    id=VENDEDOR_ID,
                    email="vendedor@joyeria.com",
                    full_name="Vendedor",
                    role=Role.VENDEDOR,
                ),
            ]
        )
        await session.commit()

    yield factory
    await engine.dispose()


@pytest_asyncio.fixture()
async def client(session_factory):
    async def override_db():
        async with session_factory() as session:
            yield session

    def as_admin():
        return TokenClaims(user_id=str(ADMIN_ID), email="admin@joyeria.com", role="admin")

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_claims] = as_admin
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


def as_vendedor():
    return TokenClaims(
        user_id=str(VENDEDOR_ID), email="vendedor@joyeria.com", role="vendedor"
    )


async def test_get_lazily_creates_single_global_company_settings(client, session_factory):
    first = await client.get("/api/v1/settings/company")
    second = await client.get("/api/v1/settings/company")

    assert first.status_code == 200, first.text
    assert first.json() == {
        "business_name": "",
        "rfc": "",
        "fiscal_address": "",
        "phone": "",
        "email": "",
    }
    assert second.json() == first.json()

    async with session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(CompanySettings))
    assert count == 1


async def test_admin_updates_company_settings_with_mexico_normalization(client):
    response = await client.patch(
        "/api/v1/settings/company",
        json={
            "business_name": "  Joyería La Perla  ",
            "rfc": " jpe850101abc ",
            "fiscal_address": "  Av. Juárez 123, Centro, CDMX  ",
            "phone": " +52 (55) 1234-5678 ",
            "email": " CONTACTO@JOYERIAPERLA.MX ",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "business_name": "Joyería La Perla",
        "rfc": "JPE850101ABC",
        "fiscal_address": "Av. Juárez 123, Centro, CDMX",
        "phone": "5512345678",
        "email": "contacto@joyeriaperla.mx",
    }
    assert (await client.get("/api/v1/settings/company")).json() == response.json()


async def test_non_admin_can_read_but_cannot_modify_company_settings(client):
    app.dependency_overrides[get_current_claims] = as_vendedor

    read = await client.get("/api/v1/settings/company")
    denied = await client.patch(
        "/api/v1/settings/company", json={"business_name": "No autorizado"}
    )

    assert read.status_code == 200
    assert denied.status_code == 403


async def test_company_settings_patch_is_partial_and_rejects_unknown_fields(client):
    created = await client.patch(
        "/api/v1/settings/company",
        json={"business_name": "La Perla", "email": "ventas@laperla.mx"},
    )
    assert created.status_code == 200, created.text

    updated = await client.patch(
        "/api/v1/settings/company", json={"phone": "33 1234 5678"}
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["business_name"] == "La Perla"
    assert updated.json()["email"] == "ventas@laperla.mx"
    assert updated.json()["phone"] == "3312345678"

    unknown = await client.patch(
        "/api/v1/settings/company", json={"runtime_environment": "production"}
    )
    assert unknown.status_code == 422


async def test_company_settings_reject_invalid_mexico_profile_values(client):
    invalid_payloads = [
        {"business_name": "   "},
        {"rfc": "NOT-AN-RFC"},
        {"rfc": "JPE991332ABC"},
        {"phone": "12345"},
        {"phone": "+1 202 555 0100"},
        {"phone": "call-me-5512345678"},
        {"email": "correo-invalido"},
        {"email": "a..b@example.com"},
        {"email": ".user@example.com"},
        {"email": "user@example..com"},
    ]

    for payload in invalid_payloads:
        response = await client.patch("/api/v1/settings/company", json=payload)
        assert response.status_code == 422, (payload, response.text)
