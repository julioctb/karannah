from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import CheckConstraint, MetaData, Table, UniqueConstraint

from app import models
from app.models import StockTransfer, StockTransferLine, StockTransferStatus
from app.models.inventory import StockEntry


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
