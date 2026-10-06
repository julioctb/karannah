from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import MetaData, Table, UniqueConstraint, create_engine
from sqlalchemy.orm import Session

from app import models
from app.core.db import Base
from app.schemas.repairs import RepairRead


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


def test_api_contract_documents_repair_foundations_without_future_endpoints():
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
    assert "enviado" not in repair_section
    assert "cost" not in repair_section
    assert "POST /repairs" not in repair_section
