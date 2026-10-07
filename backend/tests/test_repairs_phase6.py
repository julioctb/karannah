from __future__ import annotations

import importlib.util
import uuid
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import MetaData, Table, UniqueConstraint, create_engine, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import models
from app.api.deps import get_current_claims
from app.core.db import Base, get_db
from app.core.security import TokenClaims
from app.main import app
from app.schemas.repairs import RepairRead

ADMIN_ID = uuid.uuid4()
SELLER_ID = uuid.uuid4()
BRANCH_T01 = uuid.uuid4()
BRANCH_T02 = uuid.uuid4()


@pytest_asyncio.fixture()
async def repair_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        session.add_all(
            [
                models.Branch(id=BRANCH_T01, code="T01", name="Centro"),
                models.Branch(id=BRANCH_T02, code="T02", name="Norte"),
                models.UserProfile(
                    id=ADMIN_ID,
                    email="admin-repairs@example.com",
                    full_name="Admin",
                    role=models.Role.ADMIN,
                ),
                models.UserProfile(
                    id=SELLER_ID,
                    email="seller-repairs@example.com",
                    full_name="Seller",
                    role=models.Role.VENDEDOR,
                ),
                models.Client(
                    id=101,
                    name="María Registrada",
                    type=models.ClientType.MENUDEO,
                    active=True,
                ),
                models.Client(
                    id=102,
                    name="Cliente Inactivo",
                    type=models.ClientType.MENUDEO,
                    active=False,
                ),
            ]
        )
        await session.flush()
        session.add(
            models.UserBranchAssignment(user_id=SELLER_ID, branch_id=BRANCH_T01)
        )
        await session.commit()

    yield factory
    await engine.dispose()


@pytest_asyncio.fixture()
async def repair_client(repair_session_factory):
    async def override_db():
        async with repair_session_factory() as session:
            yield session

    async def as_seller():
        return TokenClaims(
            user_id=str(SELLER_ID), email="seller-repairs@example.com", role=None
        )

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_claims] = as_seller
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


def _intake_payload(**changes):
    payload = {
        "branch_id": str(BRANCH_T01),
        "client_id": 101,
        "product_description": "Anillo de oro",
        "service": "Ajuste de talla",
        "price": "450.00",
        "received_at": "2026-03-01",
        "expected_at": "2026-03-08",
        "notes": "Conservar grabado",
    }
    payload.update(changes)
    return payload


def test_repair_model_uses_phase6_service_vocabulary_and_operational_foundations():
    assert [(status.name, status.value) for status in models.RepairStatus] == [
        ("RECEIVED", "received"),
        ("IN_WORKSHOP", "in_workshop"),
        ("READY", "ready"),
    ]
    for legacy_value in (
        "recibido",
        "pendiente_taller",
        "en_proceso",
        "terminado",
        "enviado",
    ):
        with pytest.raises(ValueError):
            models.RepairStatus(legacy_value)
    assert not hasattr(models.RepairStatus, "RECIBIDO")

    table = models.Repair.__table__
    assert list(table.c.keys()) == [
        "id",
        "folio",
        "branch_id",
        "client_id",
        "client_name",
        "product_description",
        "service",
        "status",
        "price",
        "received_at",
        "expected_at",
        "completed_at",
        "notes",
        "sale_id",
        "delivered_at",
        "blocked_for_review",
    ]
    assert next(iter(table.c.branch_id.foreign_keys)).target_fullname == "branches.id"
    assert table.c.client_id.nullable is True
    assert table.c.client_name.nullable is False
    assert table.c.sale_id.nullable is True
    assert next(iter(table.c.sale_id.foreign_keys)).target_fullname == "sales.id"
    assert table.c.delivered_at.nullable is True
    assert table.c.blocked_for_review.default.arg is False
    assert not hasattr(models.Repair, "cost")
    assert not hasattr(models.Repair, "cost_price")
    assert not hasattr(models.Repair, "quoted_price")
    assert "price" in RepairRead.model_fields
    assert "quoted_price" not in RepairRead.model_fields

    checks = {constraint.name for constraint in table.constraints}
    assert "ck_repairs_folio_prefix" in checks
    assert "ck_repairs_price_nonnegative" in checks
    uniques = {
        constraint.name: tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert uniques["uq_repairs_sale_id"] == ("sale_id",)


def test_repair_status_history_shape_and_relationships_are_append_only():
    table = models.RepairStatusHistory.__table__
    assert list(table.c.keys()) == [
        "id",
        "repair_id",
        "from_status",
        "to_status",
        "actor_id",
        "created_at",
        "note",
    ]
    assert table.c.from_status.nullable is True
    assert table.c.to_status.nullable is False
    assert next(iter(table.c.actor_id.foreign_keys)).target_fullname == "user_profiles.id"
    assert models.Repair.history.property.back_populates == "repair"
    assert models.RepairStatusHistory.repair.property.back_populates == "history"

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        branch = models.Branch(code="T01", name="Centro")
        actor = models.UserProfile(
            email="actor@example.com", full_name="Actor", role=models.Role.ADMIN
        )
        session.add_all([branch, actor])
        session.flush()
        repair = models.Repair(
            folio="RP-T01-2026-0001",
            branch_id=branch.id,
            client_name="Cliente libre",
            product_description="Anillo",
            service="Soldadura",
            status=models.RepairStatus.RECEIVED,
            price=150,
            received_at=date(2026, 1, 2),
        )
        session.add(repair)
        session.flush()
        history = models.RepairStatusHistory(
            repair_id=repair.id,
            from_status=None,
            to_status=models.RepairStatus.RECEIVED,
            actor_id=actor.id,
        )
        session.add(history)
        session.commit()

        history.note = "attempted rewrite"
        with pytest.raises(ValueError, match="append-only"):
            session.commit()
        session.rollback()

        session.delete(history)
        with pytest.raises(ValueError, match="append-only"):
            session.commit()


def test_phase6_migration_matches_history_model_and_status_vocabulary(monkeypatch):
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0009_phase6_repairs.py"
    )
    spec = importlib.util.spec_from_file_location("phase6_repairs_migration", migration_path)
    assert spec and spec.loader
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    class OperationRecorder:
        def __init__(self):
            self.tables: dict[str, Table] = {}
            self.executed: list[str] = []

        def get_bind(self):
            return None

        def create_table(self, name, *elements):
            table = Table(name, MetaData(), *elements)
            self.tables[name] = table
            return table

        def create_index(self, *args, **kwargs):
            return None

        def add_column(self, *args, **kwargs):
            return None

        def alter_column(self, *args, **kwargs):
            return None

        def create_foreign_key(self, *args, **kwargs):
            return None

        def create_unique_constraint(self, *args, **kwargs):
            return None

        def drop_constraint(self, *args, **kwargs):
            return None

        def create_check_constraint(self, *args, **kwargs):
            return None

        def execute(self, statement):
            self.executed.append(str(statement))

    recorder = OperationRecorder()
    monkeypatch.setattr(migration, "op", recorder)
    monkeypatch.setattr(migration.postgresql.ENUM, "create", lambda *args, **kwargs: None)
    migration.upgrade()

    assert migration.revision == "0009_phase6_repairs"
    assert migration.down_revision == "0008_phase5_physical_counts"
    assert recorder.tables.keys() == {"repair_status_history"}

    history_model = models.RepairStatusHistory.__table__
    migration_table = recorder.tables["repair_status_history"]
    assert list(migration_table.c.keys()) == list(history_model.c.keys())
    assert migration_table.c.from_status.type.enums == ["received", "in_workshop", "ready"]
    assert migration_table.c.to_status.type.enums == ["received", "in_workshop", "ready"]

    sql = "\n".join(recorder.executed)
    assert "'recibido' THEN 'received'" in sql
    assert "'terminado' THEN 'ready'" in sql
    assert "ELSE 'in_workshop'" in sql
    assert "ENABLE ROW LEVEL SECURITY" in sql
    assert "CREATE OR REPLACE FUNCTION prevent_repair_status_history_mutation()" in sql
    assert "BEFORE UPDATE OR DELETE ON repair_status_history" in sql
    assert "repair status history is append-only" in sql


def test_phase6_migration_downgrade_clears_default_and_removes_append_only_objects():
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0009_phase6_repairs.py"
    )
    source = migration_path.read_text()

    clear_default = 'op.alter_column("repairs", "status", server_default=None)'
    convert_to_text = (
        'op.execute("ALTER TABLE repairs ALTER COLUMN status TYPE VARCHAR USING status::text")'
    )
    downgrade = source.split("def downgrade() -> None:", 1)[1]
    assert downgrade.index(clear_default) < downgrade.index(convert_to_text)
    assert downgrade.index("DROP TRIGGER IF EXISTS") < downgrade.index(
        'op.drop_table("repair_status_history")'
    )
    assert downgrade.index("DROP FUNCTION IF EXISTS") < downgrade.index(
        'op.drop_table("repair_status_history")'
    )


def test_api_contract_documents_repair_foundations_and_transitions():
    contract = Path(__file__).resolve().parents[2].joinpath("docs", "API_CONTRACT.md").read_text()

    for text in (
        "RP-SUC-AÑO-NÚMERO",
        "received",
        "in_workshop",
        "ready",
        "branch_id",
        "client_id",
        "client_name",
        "price",
        "sale_id",
        "paid_amount",
        "balance",
        "delivered_at",
        "blocked_for_review",
        "repair_status_history",
    ):
        assert text in contract

    repair_section = contract.split("## Reparaciones", 1)[1].split("## ", 1)[0]
    assert "POST /repairs/{repair_id}/transition" in repair_section
    assert "ready` → `in_workshop" in repair_section
    assert "nota/razon no vacia" in repair_section
    assert "no cobra, no marca pago y no entrega" in repair_section
    assert "enviado" not in repair_section
    assert "cost" not in repair_section


@pytest.mark.asyncio
async def test_create_repair_is_atomic_canonical_and_idempotent(
    repair_client, repair_session_factory
):
    headers = {"Idempotency-Key": "repair-intake-1"}
    first = await repair_client.post(
        "/api/v1/repairs", json=_intake_payload(), headers=headers
    )
    assert first.status_code == 201, first.text
    created = first.json()
    assert created == {
        "id": created["id"],
        "folio": "RP-T01-2026-000001",
        "client_id": 101,
        "client_name": "María Registrada",
        "product_description": "Anillo de oro",
        "service": "Ajuste de talla",
        "status": "received",
        "price": "450.00",
        "received_at": "2026-03-01",
        "expected_at": "2026-03-08",
        "completed_at": None,
        "notes": "Conservar grabado",
    }

    repeated = await repair_client.post(
        "/api/v1/repairs", json=_intake_payload(), headers=headers
    )
    assert repeated.status_code == 201
    assert repeated.json() == created
    changed = await repair_client.post(
        "/api/v1/repairs",
        json=_intake_payload(service="Pulido"),
        headers=headers,
    )
    assert changed.status_code == 409

    async with repair_session_factory() as session:
        repairs = list((await session.scalars(select(models.Repair))).all())
        history = list((await session.scalars(select(models.RepairStatusHistory))).all())
        assert len(repairs) == 1
        assert len(history) == 1
        assert history[0].repair_id == repairs[0].id
        assert history[0].from_status is None
        assert history[0].to_status == models.RepairStatus.RECEIVED
        assert history[0].actor_id == SELLER_ID


@pytest.mark.asyncio
async def test_create_repair_validates_customer_branch_dates_and_input(repair_client):
    assert (
        await repair_client.post("/api/v1/repairs", json=_intake_payload())
    ).status_code == 422
    assert (
        await repair_client.post(
            "/api/v1/repairs",
            json=_intake_payload(branch_id=str(BRANCH_T02)),
            headers={"Idempotency-Key": "hidden-branch"},
        )
    ).status_code == 404
    assert (
        await repair_client.post(
            "/api/v1/repairs",
            json=_intake_payload(client_id=999),
            headers={"Idempotency-Key": "unknown-client"},
        )
    ).status_code == 404
    assert (
        await repair_client.post(
            "/api/v1/repairs",
            json=_intake_payload(client_id=102),
            headers={"Idempotency-Key": "inactive-client"},
        )
    ).status_code == 404

    invalid_payloads = [
        _intake_payload(client_id=None, client_name="Cliente libre"),
        _intake_payload(price="-0.01"),
        _intake_payload(product_description="  "),
        _intake_payload(service="  "),
        _intake_payload(received_at="2026-03-09", expected_at="2026-03-08"),
        _intake_payload(status="ready"),
        _intake_payload(sale_id=1),
    ]
    for index, payload in enumerate(invalid_payloads):
        response = await repair_client.post(
            "/api/v1/repairs",
            json=payload,
            headers={"Idempotency-Key": f"invalid-{index}"},
        )
        assert response.status_code == 422, (payload, response.text)

    accepted = await repair_client.post(
        "/api/v1/repairs",
        json=_intake_payload(
            client_id=None,
            client_name="  Cliente libre  ",
            confirm_free_text_client=True,
            price=None,
        ),
        headers={"Idempotency-Key": "free-text-confirmed"},
    )
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["client_name"] == "Cliente libre"
    assert accepted.json()["price"] is None


@pytest.mark.asyncio
async def test_repair_update_changes_only_intake_fields_and_respects_lifecycle(
    repair_client, repair_session_factory
):
    created = await repair_client.post(
        "/api/v1/repairs",
        json=_intake_payload(),
        headers={"Idempotency-Key": "repair-to-update"},
    )
    repair_id = created.json()["id"]
    update = {
        "client_id": None,
        "client_name": "Cliente corregido",
        "confirm_free_text_client": True,
        "product_description": "Anillo con piedra",
        "service": "Ajuste y pulido",
        "price": "500.00",
        "received_at": "2026-03-02",
        "expected_at": None,
        "notes": None,
    }
    changed = await repair_client.patch(f"/api/v1/repairs/{repair_id}", json=update)
    assert changed.status_code == 200, changed.text
    assert changed.json()["client_id"] is None
    assert changed.json()["client_name"] == "Cliente corregido"
    assert changed.json()["status"] == "received"
    assert changed.json()["price"] == "500.00"
    assert changed.json()["expected_at"] is None

    repeated = await repair_client.patch(f"/api/v1/repairs/{repair_id}", json=update)
    assert repeated.status_code == 200
    assert repeated.json() == changed.json()
    for forbidden in (
        {"status": "ready"},
        {"branch_id": str(BRANCH_T02)},
        {"sale_id": 1},
        {"delivered_at": "2026-03-03T00:00:00Z"},
        {"blocked_for_review": True},
    ):
        response = await repair_client.patch(
            f"/api/v1/repairs/{repair_id}", json=forbidden
        )
        assert response.status_code == 422, (forbidden, response.text)

    async with repair_session_factory() as session:
        repair = await session.get(models.Repair, repair_id)
        assert repair is not None
        repair.blocked_for_review = True
        await session.commit()
    assert (
        await repair_client.patch(
            f"/api/v1/repairs/{repair_id}", json={"notes": "No permitido"}
        )
    ).status_code == 409

    async with repair_session_factory() as session:
        repair = await session.get(models.Repair, repair_id)
        assert repair is not None
        repair.blocked_for_review = False
        repair.delivered_at = datetime(2026, 3, 10, tzinfo=UTC)
        await session.commit()
    assert (
        await repair_client.patch(
            f"/api/v1/repairs/{repair_id}", json={"notes": "Tampoco permitido"}
        )
    ).status_code == 409


@pytest.mark.asyncio
async def test_repairs_are_globally_readable_but_hidden_branch_is_not_mutable(
    repair_client, repair_session_factory
):
    async with repair_session_factory() as session:
        hidden = models.Repair(
            folio="RP-T02-2026-000001",
            branch_id=BRANCH_T02,
            client_name="Global",
            product_description="Cadena",
            service="Soldadura",
            status=models.RepairStatus.RECEIVED,
            received_at=date(2026, 3, 1),
        )
        session.add(hidden)
        await session.commit()
        await session.refresh(hidden)
        hidden_id = hidden.id

    listed = await repair_client.get("/api/v1/repairs")
    assert listed.status_code == 200
    assert any(row["id"] == hidden_id for row in listed.json())
    assert (
        await repair_client.patch(
            f"/api/v1/repairs/{hidden_id}", json={"notes": "Sin alcance"}
        )
    ).status_code == 404


@pytest.mark.asyncio
async def test_repair_status_transition_lifecycle_appends_actor_history_atomically(
    repair_client, repair_session_factory
):
    created = await repair_client.post(
        "/api/v1/repairs",
        json=_intake_payload(),
        headers={"Idempotency-Key": "repair-transition-lifecycle"},
    )
    repair_id = created.json()["id"]

    started = await repair_client.post(
        f"/api/v1/repairs/{repair_id}/transition",
        json={"to_status": "in_workshop", "note": "  Inicia diagnostico  "},
    )
    assert started.status_code == 200, started.text
    assert started.json()["status"] == "in_workshop"
    assert started.json()["completed_at"] is None

    ready = await repair_client.post(
        f"/api/v1/repairs/{repair_id}/transition",
        json={"to_status": "ready", "note": "Trabajo concluido"},
    )
    assert ready.status_code == 200, ready.text
    assert ready.json()["status"] == "ready"
    assert ready.json()["completed_at"] is not None

    reopened = await repair_client.post(
        f"/api/v1/repairs/{repair_id}/transition",
        json={"to_status": "in_workshop", "note": "Cliente reporta ajuste pendiente"},
    )
    assert reopened.status_code == 200, reopened.text
    assert reopened.json()["status"] == "in_workshop"
    assert reopened.json()["completed_at"] == ready.json()["completed_at"]

    ready_again = await repair_client.post(
        f"/api/v1/repairs/{repair_id}/transition",
        json={"to_status": "ready"},
    )
    assert ready_again.status_code == 200, ready_again.text
    assert ready_again.json()["completed_at"] == ready.json()["completed_at"]

    async with repair_session_factory() as session:
        repair = await session.get(models.Repair, repair_id)
        history = list(
            (
                await session.scalars(
                    select(models.RepairStatusHistory)
                    .where(models.RepairStatusHistory.repair_id == repair_id)
                    .order_by(models.RepairStatusHistory.created_at, models.RepairStatusHistory.id)
                )
            ).all()
        )
        assert repair is not None
        assert repair.status == models.RepairStatus.READY
        assert repair.sale_id is None
        assert repair.delivered_at is None
        assert repair.blocked_for_review is False
        assert len(history) == 5
        assert {
            (row.from_status, row.to_status, row.note) for row in history
        } == {
            (None, models.RepairStatus.RECEIVED, None),
            (
                models.RepairStatus.RECEIVED,
                models.RepairStatus.IN_WORKSHOP,
                "Inicia diagnostico",
            ),
            (
                models.RepairStatus.IN_WORKSHOP,
                models.RepairStatus.READY,
                "Trabajo concluido",
            ),
            (
                models.RepairStatus.READY,
                models.RepairStatus.IN_WORKSHOP,
                "Cliente reporta ajuste pendiente",
            ),
            (models.RepairStatus.IN_WORKSHOP, models.RepairStatus.READY, None),
        }
        assert {row.actor_id for row in history} == {SELLER_ID}


@pytest.mark.asyncio
async def test_repair_status_transition_rejects_invalid_noop_and_missing_reopen_reason(
    repair_client, repair_session_factory
):
    created = await repair_client.post(
        "/api/v1/repairs",
        json=_intake_payload(),
        headers={"Idempotency-Key": "repair-transition-invalid"},
    )
    repair_id = created.json()["id"]

    invalid_requests = [
        ({"to_status": "ready"}, 409),
        ({"to_status": "received"}, 409),
        ({"to_status": "unknown"}, 422),
    ]
    for payload, expected_status in invalid_requests:
        response = await repair_client.post(
            f"/api/v1/repairs/{repair_id}/transition", json=payload
        )
        assert response.status_code == expected_status, (payload, response.text)

    assert (
        await repair_client.post(
            f"/api/v1/repairs/{repair_id}/transition",
            json={"to_status": "in_workshop"},
        )
    ).status_code == 200
    assert (
        await repair_client.post(
            f"/api/v1/repairs/{repair_id}/transition",
            json={"to_status": "received"},
        )
    ).status_code == 409
    assert (
        await repair_client.post(
            f"/api/v1/repairs/{repair_id}/transition", json={"to_status": "ready"}
        )
    ).status_code == 200

    for missing_reason in (None, "", "   "):
        response = await repair_client.post(
            f"/api/v1/repairs/{repair_id}/transition",
            json={"to_status": "in_workshop", "note": missing_reason},
        )
        assert response.status_code == 422, response.text

    async with repair_session_factory() as session:
        history = list(
            (
                await session.scalars(
                    select(models.RepairStatusHistory).where(
                        models.RepairStatusHistory.repair_id == repair_id
                    )
                )
            ).all()
        )
        assert len(history) == 3


@pytest.mark.asyncio
async def test_repair_status_transition_rejects_hidden_delivered_and_blocked_repairs(
    repair_client, repair_session_factory
):
    async with repair_session_factory() as session:
        hidden = models.Repair(
            folio="RP-T02-2026-000002",
            branch_id=BRANCH_T02,
            client_name="Oculta",
            product_description="Cadena",
            service="Soldadura",
            status=models.RepairStatus.RECEIVED,
            received_at=date(2026, 3, 1),
        )
        delivered = models.Repair(
            folio="RP-T01-2026-000002",
            branch_id=BRANCH_T01,
            client_name="Entregada",
            product_description="Anillo",
            service="Pulido",
            status=models.RepairStatus.READY,
            received_at=date(2026, 3, 1),
            delivered_at=datetime(2026, 3, 5, tzinfo=UTC),
        )
        blocked = models.Repair(
            folio="RP-T01-2026-000003",
            branch_id=BRANCH_T01,
            client_name="Bloqueada",
            product_description="Pulsera",
            service="Ajuste",
            status=models.RepairStatus.RECEIVED,
            received_at=date(2026, 3, 1),
            blocked_for_review=True,
        )
        session.add_all([hidden, delivered, blocked])
        await session.commit()
        ids = hidden.id, delivered.id, blocked.id

    hidden_response = await repair_client.post(
        f"/api/v1/repairs/{ids[0]}/transition", json={"to_status": "in_workshop"}
    )
    delivered_response = await repair_client.post(
        f"/api/v1/repairs/{ids[1]}/transition",
        json={"to_status": "in_workshop", "note": "No debe reabrir"},
    )
    blocked_response = await repair_client.post(
        f"/api/v1/repairs/{ids[2]}/transition", json={"to_status": "in_workshop"}
    )
    assert hidden_response.status_code == 404
    assert delivered_response.status_code == 409
    assert blocked_response.status_code == 409

    async with repair_session_factory() as session:
        history = list((await session.scalars(select(models.RepairStatusHistory))).all())
        assert history == []
