from __future__ import annotations

import importlib.util
import sqlite3
import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import CheckConstraint, MetaData, Table, UniqueConstraint, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import models
from app.api.deps import get_current_claims
from app.core.db import Base, get_db
from app.core.security import TokenClaims
from app.main import app
from app.models import (
    PhysicalCount,
    PhysicalCountStatus,
    StockTransfer,
    StockTransferLine,
    StockTransferStatus,
)
from app.models.catalog import Category, Product, ProductGroup, ProductStatus, ProductVariant
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile
from app.models.inventory import (
    PhysicalCountLine,
    StockBalance,
    StockEntry,
    StockMovementType,
)
from app.models.sales import FolioCounter


def _transfer_quantity_database() -> sqlite3.Connection:
    checks = [
        str(constraint.sqltext)
        for constraint in StockTransferLine.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    ]
    database = sqlite3.connect(":memory:")
    database.execute(
        "CREATE TABLE transfer_quantities ("
        "shipped_quantity INTEGER NOT NULL, "
        "received_quantity INTEGER, "
        "shortage_quantity INTEGER, "
        + ", ".join(f"CHECK ({expression})" for expression in checks)
        + ")"
    )
    return database


@pytest.mark.parametrize(
    ("shipped", "received", "shortage", "accepted"),
    [
        pytest.param(5, None, None, True, id="pre-reception"),
        pytest.param(5, 5, 0, True, id="exact-reception"),
        pytest.param(5, 3, 2, True, id="matching-shortage"),
        pytest.param(5, 4, None, False, id="missing-shortage"),
        pytest.param(5, None, 1, False, id="shortage-without-reception"),
        pytest.param(5, 6, 0, False, id="over-reception"),
        pytest.param(5, 3, 1, False, id="inconsistent-shortage"),
    ],
)
def test_transfer_quantity_constraints_are_enforced_by_database(
    shipped: int,
    received: int | None,
    shortage: int | None,
    accepted: bool,
):
    database = _transfer_quantity_database()
    values = (shipped, received, shortage)

    try:
        if accepted:
            database.execute("INSERT INTO transfer_quantities VALUES (?, ?, ?)", values)
        else:
            with pytest.raises(sqlite3.IntegrityError):
                database.execute("INSERT INTO transfer_quantities VALUES (?, ?, ?)", values)
    finally:
        database.close()


def test_transfer_models_expose_lifecycle_enum_tables_and_movements():
    assert [status.value for status in StockTransferStatus] == ["draft", "sent", "received"]

    assert StockTransfer.__tablename__ == "stock_transfers"
    assert StockTransferLine.__tablename__ == "stock_transfer_lines"

    assert StockEntry.__table__.c.movement_type.type.enums == [
        "inicial",
        "venta",
        "devolucion",
        "ajuste",
        "conteo",
        "transferencia_entrada",
        "transferencia_salida",
    ]


def test_transfer_model_constraints_protect_quantities_and_identity():
    transfer_checks = {constraint.name for constraint in StockTransferLine.__table__.constraints}
    assert "ck_stock_transfer_lines_shipped_quantity_positive" in transfer_checks
    assert "ck_stock_transfer_lines_received_quantity_nonnegative" in transfer_checks
    assert "ck_stock_transfer_lines_shortage_quantity_nonnegative" in transfer_checks
    assert "ck_stock_transfer_lines_received_not_over_shipped" in transfer_checks
    assert "ck_stock_transfer_lines_shortage_matches_received" in transfer_checks

    transfer_uniques = {constraint.name for constraint in StockTransferLine.__table__.constraints}
    assert "uq_stock_transfer_line_variant" in transfer_uniques


def test_transfer_migration_instantiates_constraints_aligned_with_models(monkeypatch):
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0007_phase5_transfers.py"
    )
    spec = importlib.util.spec_from_file_location("phase5_transfer_migration", migration_path)
    assert spec and spec.loader
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    class OperationRecorder:
        def __init__(self):
            self.tables: dict[str, Table] = {}

        def get_bind(self):
            return None

        def create_table(self, name, *elements):
            table = Table(name, MetaData(), *elements)
            self.tables[name] = table
            return table

        def create_index(self, *args, **kwargs):
            return None

        def execute(self, statement):
            return None

    recorder = OperationRecorder()
    monkeypatch.setattr(migration, "op", recorder)
    monkeypatch.setattr(migration.postgresql.ENUM, "create", lambda *args, **kwargs: None)
    migration.upgrade()

    assert migration.revision == "0007_phase5_transfers"
    assert migration.down_revision == "0006_sale_lifecycle_credit_ledger"

    models = {
        "stock_transfers": StockTransfer.__table__,
        "stock_transfer_lines": StockTransferLine.__table__,
    }
    assert recorder.tables.keys() == models.keys()

    for name, model_table in models.items():
        migration_table = recorder.tables[name]
        assert list(migration_table.c.keys()) == list(model_table.c.keys())
        assert {
            constraint.name: str(constraint.sqltext)
            for constraint in migration_table.constraints
            if isinstance(constraint, CheckConstraint)
        } == {
            constraint.name: str(constraint.sqltext)
            for constraint in model_table.constraints
            if isinstance(constraint, CheckConstraint)
        }
        assert {
            constraint.name: tuple(constraint.columns.keys())
            for constraint in migration_table.constraints
            if isinstance(constraint, UniqueConstraint)
        } == {
            constraint.name: tuple(constraint.columns.keys())
            for constraint in model_table.constraints
            if isinstance(constraint, UniqueConstraint)
        }

    assert recorder.tables["stock_transfers"].c.status.type.enums == [
        "draft",
        "sent",
        "received",
    ]


def test_api_contract_names_transfer_foundation_vocabulary_only():
    contract = Path(__file__).resolve().parents[2].joinpath("docs", "API_CONTRACT.md").read_text()

    assert "TR-SUC-YEAR-NUMBER" in contract
    assert "draft" in contract and "sent" in contract and "received" in contract
    assert "shipped_quantity" in contract
    assert "received_quantity" in contract
    assert "shortage_quantity" in contract


def _count_quantity_database() -> sqlite3.Connection:
    checks = [
        str(constraint.sqltext)
        for constraint in models.PhysicalCountLine.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    ]
    database = sqlite3.connect(":memory:")
    database.execute(
        "CREATE TABLE count_quantities ("
        "snapshot_quantity INTEGER NOT NULL, "
        "observed_quantity INTEGER, "
        + ", ".join(f"CHECK ({expression})" for expression in checks)
        + ")"
    )
    return database


@pytest.mark.parametrize(
    ("snapshot", "observed", "accepted"),
    [
        pytest.param(5, None, True, id="not-yet-observed"),
        pytest.param(0, 0, True, id="zero-stock-observed"),
        pytest.param(5, 3, True, id="observed-shortage"),
        pytest.param(5, 7, True, id="observed-surplus"),
        pytest.param(-1, None, False, id="negative-snapshot"),
        pytest.param(5, -1, False, id="negative-observed"),
    ],
)
def test_count_quantity_constraints_are_enforced_by_database(
    snapshot: int,
    observed: int | None,
    accepted: bool,
):
    database = _count_quantity_database()
    values = (snapshot, observed)

    try:
        if accepted:
            database.execute("INSERT INTO count_quantities VALUES (?, ?)", values)
        else:
            with pytest.raises(sqlite3.IntegrityError):
                database.execute("INSERT INTO count_quantities VALUES (?, ?)", values)
    finally:
        database.close()


def test_count_models_expose_lifecycle_enum_tables_and_relationships():
    assert [status.value for status in models.PhysicalCountStatus] == ["open", "finalized"]
    assert models.PhysicalCount.__tablename__ == "physical_counts"
    assert models.PhysicalCountLine.__tablename__ == "physical_count_lines"
    assert models.PhysicalCount.lines.property.back_populates == "count"
    assert models.PhysicalCountLine.count.property.back_populates == "lines"


def test_count_model_constraints_protect_quantities_and_identity():
    line_table = models.PhysicalCountLine.__table__
    assert list(line_table.c.keys()) == [
        "id",
        "physical_count_id",
        "variant_id",
        "snapshot_quantity",
        "observed_quantity",
    ]

    checks = {constraint.name for constraint in line_table.constraints}
    assert "ck_physical_count_lines_snapshot_quantity_nonnegative" in checks
    assert "ck_physical_count_lines_observed_quantity_nonnegative" in checks

    uniques = {
        constraint.name: tuple(constraint.columns.keys())
        for constraint in line_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert uniques["uq_physical_count_lines_physical_count_variant"] == (
        "physical_count_id",
        "variant_id",
    )


def test_count_migration_instantiates_constraints_aligned_with_models(monkeypatch):
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0008_phase5_physical_counts.py"
    )
    spec = importlib.util.spec_from_file_location("phase5_count_migration", migration_path)
    assert spec and spec.loader
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    class OperationRecorder:
        def __init__(self):
            self.tables: dict[str, Table] = {}

        def get_bind(self):
            return None

        def create_table(self, name, *elements):
            table = Table(name, MetaData(), *elements)
            self.tables[name] = table
            return table

        def create_index(self, *args, **kwargs):
            return None

        def execute(self, statement):
            return None

    recorder = OperationRecorder()
    monkeypatch.setattr(migration, "op", recorder)
    monkeypatch.setattr(migration.postgresql.ENUM, "create", lambda *args, **kwargs: None)
    migration.upgrade()

    assert migration.revision == "0008_phase5_physical_counts"
    assert migration.down_revision == "0007_phase5_transfers"

    count_models = {
        "physical_counts": models.PhysicalCount.__table__,
        "physical_count_lines": models.PhysicalCountLine.__table__,
    }
    assert recorder.tables.keys() == count_models.keys()

    for name, model_table in count_models.items():
        migration_table = recorder.tables[name]
        assert list(migration_table.c.keys()) == list(model_table.c.keys())
        assert {
            constraint.name: str(constraint.sqltext)
            for constraint in migration_table.constraints
            if isinstance(constraint, CheckConstraint)
        } == {
            constraint.name: str(constraint.sqltext)
            for constraint in model_table.constraints
            if isinstance(constraint, CheckConstraint)
        }
        assert {
            constraint.name: tuple(constraint.columns.keys())
            for constraint in migration_table.constraints
            if isinstance(constraint, UniqueConstraint)
        } == {
            constraint.name: tuple(constraint.columns.keys())
            for constraint in model_table.constraints
            if isinstance(constraint, UniqueConstraint)
        }

    assert recorder.tables["physical_counts"].c.status.type.enums == ["open", "finalized"]


def test_api_contract_names_count_foundation_vocabulary():
    contract = Path(__file__).resolve().parents[2].joinpath("docs", "API_CONTRACT.md").read_text()

    assert "CF-SUC-YEAR-NUMBER" in contract
    assert "open" in contract and "finalized" in contract
    assert "snapshot_quantity" in contract
    assert "observed_quantity" in contract
    assert "expected_quantity" not in contract
    assert "counted_quantity" not in contract
    assert "difference_quantity" not in contract


ADMIN_ID = uuid.uuid4()
MANAGER_ID = uuid.uuid4()
SELLER_ID = uuid.uuid4()
ORIGIN_ID = uuid.uuid4()
DESTINATION_ID = uuid.uuid4()


@pytest_asyncio.fixture()
async def transfer_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add_all(
            [
                Branch(id=ORIGIN_ID, code="T01", name="Origin"),
                Branch(id=DESTINATION_ID, code="T02", name="Destination"),
                UserProfile(id=ADMIN_ID, email="transfer-admin@test", role=Role.ADMIN),
                UserProfile(id=MANAGER_ID, email="transfer-manager@test", role=Role.ENCARGADO),
                UserProfile(id=SELLER_ID, email="transfer-seller@test", role=Role.VENDEDOR),
            ]
        )
        await session.flush()
        session.add_all(
            [
                UserBranchAssignment(user_id=MANAGER_ID, branch_id=ORIGIN_ID),
                Category(id=901, code="T5", name="Phase 5", group=ProductGroup.NO_JOYERIA),
            ]
        )
        await session.flush()
        session.add(
            Product(
                id=901,
                name="Transfer product",
                category_id=901,
                status=ProductStatus.DISPONIBLE,
            )
        )
        await session.flush()
        session.add_all(
            [
                ProductVariant(
                    id=901,
                    product_id=901,
                    sku="T5-001",
                    cost_price=1,
                    retail_price=2,
                    wholesale_price=1,
                ),
                ProductVariant(
                    id=902,
                    product_id=901,
                    sku="T5-002",
                    cost_price=1,
                    retail_price=2,
                    wholesale_price=1,
                ),
                ProductVariant(
                    id=903,
                    product_id=901,
                    sku="T5-003",
                    cost_price=1,
                    retail_price=2,
                    wholesale_price=1,
                    active=False,
                ),
                ProductVariant(
                    id=904,
                    product_id=901,
                    sku="T5-004",
                    cost_price=1,
                    retail_price=2,
                    wholesale_price=1,
                ),
                ProductVariant(
                    id=905,
                    product_id=901,
                    sku="T5-005",
                    cost_price=1,
                    retail_price=2,
                    wholesale_price=1,
                ),
                StockBalance(branch_id=ORIGIN_ID, variant_id=901, quantity=10),
                StockBalance(branch_id=ORIGIN_ID, variant_id=902, quantity=2),
                StockBalance(branch_id=ORIGIN_ID, variant_id=903, quantity=8),
                StockBalance(branch_id=ORIGIN_ID, variant_id=904, quantity=0),
            ]
        )
        await session.commit()
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture()
async def transfer_client(transfer_session_factory):
    async def override_db():
        async with transfer_session_factory() as session:
            yield session

    def as_admin():
        return TokenClaims(user_id=str(ADMIN_ID), email="transfer-admin@test", role="admin")

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_claims] = as_admin
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


def _create_payload(lines=None):
    return {
        "origin_branch_id": str(ORIGIN_ID),
        "destination_branch_id": str(DESTINATION_ID),
        "lines": lines or [{"variant_id": 901, "shipped_quantity": 5}],
    }


async def _create_transfer(client: AsyncClient, lines=None) -> dict:
    response = await client.post("/api/v1/inventory/transfers", json=_create_payload(lines))
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_list_and_detail_transfer(transfer_client, transfer_session_factory):
    created = await _create_transfer(
        transfer_client,
        [
            {"variant_id": 902, "shipped_quantity": 1},
            {"variant_id": 901, "shipped_quantity": 5},
        ],
    )
    assert created["folio"].startswith("TR-T01-")
    assert created["folio"].endswith("-000001")
    assert created["status"] == "draft"
    assert created["created_by"] == str(ADMIN_ID)
    assert [line["variant_id"] for line in created["lines"]] == [901, 902]

    listed = (await transfer_client.get("/api/v1/inventory/transfers")).json()
    assert [item["id"] for item in listed] == [created["id"]]
    detail = await transfer_client.get(f"/api/v1/inventory/transfers/{created['id']}")
    assert detail.status_code == 200
    assert detail.json() == created

    async with transfer_session_factory() as session:
        persisted = await session.get(StockTransfer, uuid.UUID(created["id"]))
        assert persisted is not None and persisted.created_by == ADMIN_ID


@pytest.mark.parametrize(
    "payload",
    [
        _create_payload([{"variant_id": 901, "shipped_quantity": 0}]),
        {
            "origin_branch_id": str(ORIGIN_ID),
            "destination_branch_id": str(ORIGIN_ID),
            "lines": [{"variant_id": 901, "shipped_quantity": 1}],
        },
        _create_payload(
            [
                {"variant_id": 901, "shipped_quantity": 1},
                {"variant_id": 901, "shipped_quantity": 2},
            ]
        ),
        _create_payload([{"variant_id": 903, "shipped_quantity": 1}]),
        _create_payload([{"variant_id": 99999, "shipped_quantity": 1}]),
    ],
)
async def test_create_transfer_rejects_invalid_identity_or_variants(transfer_client, payload):
    response = await transfer_client.post("/api/v1/inventory/transfers", json=payload)
    assert response.status_code in {404, 409, 422}


async def test_transfer_authorization_requires_role_and_both_branches(transfer_client):
    created = await _create_transfer(transfer_client)

    def as_seller():
        return TokenClaims(user_id=str(SELLER_ID), email="transfer-seller@test", role="vendedor")

    app.dependency_overrides[get_current_claims] = as_seller
    assert (await transfer_client.get("/api/v1/inventory/transfers")).status_code == 403
    assert (
        await transfer_client.post("/api/v1/inventory/transfers", json=_create_payload())
    ).status_code == 403

    def as_manager():
        return TokenClaims(user_id=str(MANAGER_ID), email="transfer-manager@test", role="encargado")

    app.dependency_overrides[get_current_claims] = as_manager
    assert (await transfer_client.get("/api/v1/inventory/transfers")).json() == []
    assert (
        await transfer_client.get(f"/api/v1/inventory/transfers/{created['id']}")
    ).status_code == 404
    assert (
        await transfer_client.post("/api/v1/inventory/transfers", json=_create_payload())
    ).status_code == 404
    assert (
        await transfer_client.post(
            f"/api/v1/inventory/transfers/{created['id']}/send",
            json={},
            headers={"Idempotency-Key": "manager-send"},
        )
    ).status_code == 404


async def test_send_transfer_is_atomic_audited_and_idempotent(
    transfer_client, transfer_session_factory
):
    created = await _create_transfer(transfer_client)
    url = f"/api/v1/inventory/transfers/{created['id']}/send"
    headers = {"Idempotency-Key": "send-1"}
    sent = await transfer_client.post(url, json={"note": "Dispatch"}, headers=headers)
    assert sent.status_code == 200
    assert sent.json()["status"] == "sent"
    replay = await transfer_client.post(url, json={"note": "Dispatch"}, headers=headers)
    assert replay.status_code == 200 and replay.json() == sent.json()
    conflict = await transfer_client.post(url, json={"note": "Changed"}, headers=headers)
    assert conflict.status_code == 409
    assert (
        await transfer_client.post(
            url,
            json={"note": "Dispatch"},
            headers={"Idempotency-Key": "send-after-sent"},
        )
    ).status_code == 409

    async with transfer_session_factory() as session:
        balance = await session.get(StockBalance, (ORIGIN_ID, 901))
        assert balance.quantity == 5
        entries = list(
            await session.scalars(
                select(StockEntry).where(
                    StockEntry.reference == created["folio"],
                    StockEntry.movement_type == StockMovementType.TRANSFERENCIA_SALIDA,
                )
            )
        )
        assert [(entry.branch_id, entry.variant_id, entry.quantity) for entry in entries] == [
            (ORIGIN_ID, 901, -5)
        ]


async def test_send_with_insufficient_stock_changes_nothing(
    transfer_client, transfer_session_factory
):
    created = await _create_transfer(
        transfer_client, [{"variant_id": 901, "shipped_quantity": 11}]
    )
    response = await transfer_client.post(
        f"/api/v1/inventory/transfers/{created['id']}/send",
        json={},
        headers={"Idempotency-Key": "send-insufficient"},
    )
    assert response.status_code == 409
    async with transfer_session_factory() as session:
        transfer = await session.get(StockTransfer, uuid.UUID(created["id"]))
        balance = await session.get(StockBalance, (ORIGIN_ID, 901))
        entries = list(await session.scalars(select(StockEntry).where(StockEntry.reference == created["folio"])))
        assert transfer.status is StockTransferStatus.DRAFT
        assert balance.quantity == 10
        assert entries == []


async def test_receive_transfer_records_actual_shortages_and_is_idempotent(
    transfer_client, transfer_session_factory
):
    created = await _create_transfer(
        transfer_client,
        [
            {"variant_id": 901, "shipped_quantity": 5},
            {"variant_id": 902, "shipped_quantity": 2},
        ],
    )
    await transfer_client.post(
        f"/api/v1/inventory/transfers/{created['id']}/send",
        json={},
        headers={"Idempotency-Key": "send-receive"},
    )
    url = f"/api/v1/inventory/transfers/{created['id']}/receive"
    body = {
        "lines": [
            {"variant_id": 902, "received_quantity": 0},
            {"variant_id": 901, "received_quantity": 3},
        ]
    }
    headers = {"Idempotency-Key": "receive-1"}
    received = await transfer_client.post(url, json=body, headers=headers)
    assert received.status_code == 200
    assert received.json()["status"] == "received"
    assert {
        line["variant_id"]: (line["received_quantity"], line["shortage_quantity"])
        for line in received.json()["lines"]
    } == {901: (3, 2), 902: (0, 2)}
    replay = await transfer_client.post(url, json=body, headers=headers)
    assert replay.status_code == 200 and replay.json() == received.json()
    changed = {"lines": [{"variant_id": 901, "received_quantity": 4}, {"variant_id": 902, "received_quantity": 0}]}
    assert (await transfer_client.post(url, json=changed, headers=headers)).status_code == 409

    async with transfer_session_factory() as session:
        balance = await session.get(StockBalance, (DESTINATION_ID, 901))
        zero_balance = await session.get(StockBalance, (DESTINATION_ID, 902))
        assert balance.quantity == 3
        assert zero_balance is None
        entries = list(
            await session.scalars(
                select(StockEntry).where(
                    StockEntry.reference == created["folio"],
                    StockEntry.movement_type == StockMovementType.TRANSFERENCIA_ENTRADA,
                )
            )
        )
        assert [(entry.variant_id, entry.quantity) for entry in entries] == [(901, 3)]


@pytest.mark.parametrize(
    "lines",
    [
        [{"variant_id": 901, "received_quantity": 6}],
        [{"variant_id": 99999, "received_quantity": 1}],
        [],
    ],
)
async def test_receive_rejects_line_mismatches_atomically(
    transfer_client, transfer_session_factory, lines
):
    created = await _create_transfer(transfer_client)
    await transfer_client.post(
        f"/api/v1/inventory/transfers/{created['id']}/send",
        json={},
        headers={"Idempotency-Key": f"send-invalid-{len(lines)}"},
    )
    response = await transfer_client.post(
        f"/api/v1/inventory/transfers/{created['id']}/receive",
        json={"lines": lines},
        headers={"Idempotency-Key": f"receive-invalid-{lines}"},
    )
    assert response.status_code in {409, 422}
    async with transfer_session_factory() as session:
        transfer = await session.get(StockTransfer, uuid.UUID(created["id"]))
        assert transfer.status is StockTransferStatus.SENT
        assert await session.get(StockBalance, (DESTINATION_ID, 901)) is None


def test_stock_lock_helper_orders_branch_then_variant():
    from app.services.inventory import stock_balances_lock_statement

    statement = stock_balances_lock_statement(
        [(DESTINATION_ID, 902), (ORIGIN_ID, 902), (ORIGIN_ID, 901)]
    )
    order_columns = [str(clause) for clause in statement._order_by_clauses]
    assert order_columns == [
        "stock_balances.branch_id",
        "stock_balances.variant_id",
    ]


def test_api_contract_documents_transfer_workflow():
    contract = Path(__file__).resolve().parents[2].joinpath("docs", "API_CONTRACT.md").read_text()
    for text in (
        "POST /inventory/transfers",
        "GET /inventory/transfers",
        "GET /inventory/transfers/{transfer_id}",
        "POST /inventory/transfers/{transfer_id}/send",
        "POST /inventory/transfers/{transfer_id}/receive",
        "Idempotency-Key",
        "transferencia_salida",
        "transferencia_entrada",
        "409",
    ):
        assert text in contract


async def _create_count(client: AsyncClient, branch_id: uuid.UUID = ORIGIN_ID) -> dict:
    response = await client.post(
        "/api/v1/inventory/physical-counts",
        json={"branch_id": str(branch_id)},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _update_count_lines(
    client: AsyncClient, count_id: str, observations: dict[int, int]
):
    return await client.patch(
        f"/api/v1/inventory/physical-counts/{count_id}/lines",
        json={
            "lines": [
                {"variant_id": variant_id, "observed_quantity": quantity}
                for variant_id, quantity in observations.items()
            ]
        },
    )


async def test_start_count_is_idempotent_without_duplicate_document_snapshot_or_folio(
    transfer_client, transfer_session_factory
):
    url = "/api/v1/inventory/physical-counts"
    headers = {"Idempotency-Key": "start-count"}
    payload = {"branch_id": str(ORIGIN_ID)}

    missing_key = await transfer_client.post(url, json=payload)
    assert missing_key.status_code == 422

    created = await transfer_client.post(url, json=payload, headers=headers)
    assert created.status_code == 201
    replay = await transfer_client.post(url, json=payload, headers=headers)
    assert replay.status_code == 201
    assert replay.json() == created.json()

    changed = await transfer_client.post(
        url,
        json={"branch_id": str(DESTINATION_ID)},
        headers=headers,
    )
    assert changed.status_code == 409

    async with transfer_session_factory() as session:
        counts = list(await session.scalars(select(PhysicalCount)))
        lines = list(await session.scalars(select(PhysicalCountLine)))
        business_year = int(created.json()["folio"].split("-")[2])
        counter = await session.get(FolioCounter, ("CF", ORIGIN_ID, business_year))
        assert [str(count.id) for count in counts] == [created.json()["id"]]
        assert len(lines) == 3
        assert counter is not None and counter.next_value == 2


async def test_start_count_snapshots_recorded_active_balances_in_variant_order(
    transfer_client, transfer_session_factory
):
    created = await _create_count(transfer_client)

    assert created["folio"].startswith("CF-T01-")
    assert created["folio"].endswith("-000001")
    assert created["status"] == "open"
    assert created["branch_id"] == str(ORIGIN_ID)
    assert created["created_by"] == str(ADMIN_ID)
    assert [line["variant_id"] for line in created["lines"]] == [901, 902, 904]
    assert [line["snapshot_quantity"] for line in created["lines"]] == [10, 2, 0]
    assert all(line["observed_quantity"] is None for line in created["lines"])

    async with transfer_session_factory() as session:
        session.add(
            StockEntry(
                variant_id=901,
                branch_id=ORIGIN_ID,
                quantity=3,
                movement_type=StockMovementType.AJUSTE,
                created_by=ADMIN_ID,
            )
        )
        balance = await session.get(StockBalance, (ORIGIN_ID, 901))
        balance.quantity += 3
        await session.commit()

    detail = await transfer_client.get(
        f"/api/v1/inventory/physical-counts/{created['id']}"
    )
    assert detail.status_code == 200
    assert detail.json()["lines"][0]["snapshot_quantity"] == 10


async def test_count_list_detail_and_authorization(transfer_client):
    origin_count = await _create_count(transfer_client)
    destination_count = await _create_count(transfer_client, DESTINATION_ID)

    listed = await transfer_client.get("/api/v1/inventory/physical-counts")
    assert listed.status_code == 200
    assert {item["id"] for item in listed.json()} == {
        origin_count["id"],
        destination_count["id"],
    }
    detail = await transfer_client.get(
        f"/api/v1/inventory/physical-counts/{origin_count['id']}"
    )
    assert detail.status_code == 200 and detail.json() == origin_count

    def as_seller():
        return TokenClaims(user_id=str(SELLER_ID), email="transfer-seller@test", role="vendedor")

    app.dependency_overrides[get_current_claims] = as_seller
    assert (await transfer_client.get("/api/v1/inventory/physical-counts")).status_code == 403
    assert (
        await transfer_client.post(
            "/api/v1/inventory/physical-counts",
            json={"branch_id": str(ORIGIN_ID)},
            headers={"Idempotency-Key": "seller-count"},
        )
    ).status_code == 403

    def as_manager():
        return TokenClaims(
            user_id=str(MANAGER_ID), email="transfer-manager@test", role="encargado"
        )

    app.dependency_overrides[get_current_claims] = as_manager
    visible = await transfer_client.get("/api/v1/inventory/physical-counts")
    assert [item["id"] for item in visible.json()] == [origin_count["id"]]
    assert (
        await transfer_client.get(
            f"/api/v1/inventory/physical-counts/{destination_count['id']}"
        )
    ).status_code == 404
    assert (
        await transfer_client.patch(
            f"/api/v1/inventory/physical-counts/{destination_count['id']}/lines",
            json={"lines": [{"variant_id": 901, "observed_quantity": 0}]},
        )
    ).status_code == 404
    assert (
        await transfer_client.post(
            f"/api/v1/inventory/physical-counts/{destination_count['id']}/finalize",
            json={},
            headers={"Idempotency-Key": "hidden-count"},
        )
    ).status_code == 404


async def test_count_observations_are_partial_atomic_and_open_only(
    transfer_client, transfer_session_factory
):
    created = await _create_count(transfer_client)
    first = await _update_count_lines(transfer_client, created["id"], {901: 9})
    assert first.status_code == 200
    by_variant = {line["variant_id"]: line for line in first.json()["lines"]}
    assert by_variant[901]["observed_quantity"] == 9
    assert by_variant[901]["snapshot_quantity"] == 10
    assert by_variant[902]["observed_quantity"] is None

    duplicate = await transfer_client.patch(
        f"/api/v1/inventory/physical-counts/{created['id']}/lines",
        json={
            "lines": [
                {"variant_id": 901, "observed_quantity": 8},
                {"variant_id": 901, "observed_quantity": 7},
            ]
        },
    )
    unknown = await _update_count_lines(transfer_client, created["id"], {99999: 1})
    negative = await transfer_client.patch(
        f"/api/v1/inventory/physical-counts/{created['id']}/lines",
        json={"lines": [{"variant_id": 902, "observed_quantity": -1}]},
    )
    assert duplicate.status_code == 409
    assert unknown.status_code == 409
    assert negative.status_code == 422

    detail = (
        await transfer_client.get(f"/api/v1/inventory/physical-counts/{created['id']}")
    ).json()
    persisted = {line["variant_id"]: line for line in detail["lines"]}
    assert persisted[901]["observed_quantity"] == 9
    assert persisted[902]["observed_quantity"] is None

    async with transfer_session_factory() as session:
        count = await session.get(PhysicalCount, uuid.UUID(created["id"]))
        count.status = PhysicalCountStatus.FINALIZED
        await session.commit()
    assert (await _update_count_lines(transfer_client, created["id"], {901: 8})).status_code == 409


async def test_finalize_requires_every_observation(transfer_client):
    created = await _create_count(transfer_client)
    await _update_count_lines(transfer_client, created["id"], {901: 10})
    response = await transfer_client.post(
        f"/api/v1/inventory/physical-counts/{created['id']}/finalize",
        json={},
        headers={"Idempotency-Key": "incomplete-count"},
    )
    assert response.status_code == 409


async def test_finalize_reconciles_current_balance_and_is_idempotent(
    transfer_client, transfer_session_factory
):
    created = await _create_count(transfer_client)
    updated = await _update_count_lines(
        transfer_client, created["id"], {901: 12, 902: 1, 904: 0}
    )
    assert updated.status_code == 200

    async with transfer_session_factory() as session:
        first = await session.get(StockBalance, (ORIGIN_ID, 901))
        second = await session.get(StockBalance, (ORIGIN_ID, 902))
        first.quantity = 11
        second.quantity = 4
        await session.commit()

    url = f"/api/v1/inventory/physical-counts/{created['id']}/finalize"
    headers = {"Idempotency-Key": "finalize-count"}
    finalized = await transfer_client.post(url, json={}, headers=headers)
    assert finalized.status_code == 200
    assert finalized.json()["status"] == "finalized"
    assert finalized.json()["finalized_by"] == str(ADMIN_ID)
    replay = await transfer_client.post(url, json={}, headers=headers)
    assert replay.status_code == 200 and replay.json() == finalized.json()
    assert (
        await transfer_client.post(url, json={"note": "changed"}, headers=headers)
    ).status_code == 409
    assert (
        await transfer_client.post(
            url, json={}, headers={"Idempotency-Key": "new-finalize-key"}
        )
    ).status_code == 409
    assert (await _update_count_lines(transfer_client, created["id"], {901: 11})).status_code == 409

    async with transfer_session_factory() as session:
        balances = {
            variant_id: (await session.get(StockBalance, (ORIGIN_ID, variant_id))).quantity
            for variant_id in (901, 902, 904)
        }
        assert balances == {901: 12, 902: 1, 904: 0}
        entries = list(
            await session.scalars(
                select(StockEntry)
                .where(
                    StockEntry.reference == created["folio"],
                    StockEntry.movement_type == StockMovementType.CONTEO,
                )
                .order_by(StockEntry.variant_id)
            )
        )
        assert [
            (entry.variant_id, entry.quantity, entry.created_by) for entry in entries
        ] == [(901, 1, ADMIN_ID), (902, -3, ADMIN_ID)]


async def test_finalize_reconciles_when_current_balance_is_below_snapshot(
    transfer_client, transfer_session_factory
):
    created = await _create_count(transfer_client)
    await _update_count_lines(
        transfer_client, created["id"], {901: 0, 902: 4, 904: 0}
    )
    async with transfer_session_factory() as session:
        first = await session.get(StockBalance, (ORIGIN_ID, 901))
        first.quantity = 5
        await session.commit()

    response = await transfer_client.post(
        f"/api/v1/inventory/physical-counts/{created['id']}/finalize",
        json={},
        headers={"Idempotency-Key": "negative-count"},
    )
    assert response.status_code == 200

    async with transfer_session_factory() as session:
        count = await session.get(PhysicalCount, uuid.UUID(created["id"]))
        balances = {
            variant_id: (await session.get(StockBalance, (ORIGIN_ID, variant_id))).quantity
            for variant_id in (901, 902, 904)
        }
        entries = list(
            await session.scalars(
                select(StockEntry)
                .where(StockEntry.reference == created["folio"])
                .order_by(StockEntry.variant_id)
            )
        )
        assert count.status is PhysicalCountStatus.FINALIZED
        assert balances == {901: 0, 902: 4, 904: 0}
        assert [(entry.variant_id, entry.quantity) for entry in entries] == [
            (901, -5),
            (902, 2),
        ]


async def test_count_update_rejects_empty_lines(transfer_client):
    created = await _create_count(transfer_client)
    response = await transfer_client.patch(
        f"/api/v1/inventory/physical-counts/{created['id']}/lines", json={"lines": []}
    )
    assert response.status_code == 422


def test_api_contract_documents_physical_count_workflow():
    contract = Path(__file__).resolve().parents[2].joinpath("docs", "API_CONTRACT.md").read_text()
    for text in (
        "POST /inventory/physical-counts",
        "GET /inventory/physical-counts",
        "GET /inventory/physical-counts/{count_id}",
        "PATCH /inventory/physical-counts/{count_id}/lines",
        "POST /inventory/physical-counts/{count_id}/finalize",
        "Idempotency-Key",
        "conteo",
        "snapshot_quantity",
        "observed_quantity",
        "201",
        "409",
        "422",
    ):
        assert text in contract
