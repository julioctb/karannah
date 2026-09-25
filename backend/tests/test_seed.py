from decimal import Decimal

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.db import Base
from app.models.catalog import Category, Collection, Material, Product, Subcategory
from app.models.clients import Client, CreditEntry
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile
from app.models.inventory import StockEntry
from app.models.repairs import Repair
from app.models.sales import Sale
from app.seed import _load_data, _wipe, seed


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)

    @event.listens_for(engine.sync_engine, "connect")
    def _fk_on(dbapi_conn, _):  # type: ignore[no-untyped-def]
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as sess:
        yield sess
    await engine.dispose()


async def test_seed_full_dataset(session: AsyncSession) -> None:
    data = _load_data()
    await seed(session, data)
    await session.commit()

    counts = {
        Branch: 3,
        Category: 11,
        Material: 6,
        Collection: 10,
        Product: 19,
        Sale: 12,
        Repair: 5,
    }
    for model, expected in counts.items():
        n = await session.scalar(select(func.count()).select_from(model))
        assert n == expected, model

    n_subs = await session.scalar(select(func.count()).select_from(Subcategory))
    expected_subs = sum(len(s) for s in data["SUBCATEGORIAS_SEED"].values())
    assert n_subs == expected_subs

    # Las identidades reales se aprovisionan fuera del dataset demo.
    n_users = await session.scalar(select(func.count()).select_from(UserProfile))
    assert n_users == 0
    n_assign = await session.scalar(select(func.count()).select_from(UserBranchAssignment))
    assert n_assign == 0


async def test_stock_is_inicial_snapshot_in_t01(session: AsyncSession) -> None:
    await seed(session, _load_data())
    t01 = await session.scalar(select(Branch).where(Branch.code == "T01"))
    total = await session.scalar(select(func.sum(StockEntry.quantity)))
    expected = sum(p["stock"] for p in _load_data()["PRODUCTOS"])
    assert total == expected
    branches = (
        await session.execute(select(StockEntry.branch_id, StockEntry.movement_type).distinct())
    ).all()
    assert {(b, mt) for b, mt in branches} == {(t01.id, "inicial")}


async def test_credit_balances_match_demo_saldos(session: AsyncSession) -> None:
    data = _load_data()
    await seed(session, data)

    for c in data["CLIENTES"]:
        client_id = await session.scalar(select(Client.id).where(Client.name == c["nombre"]))
        balance = await session.scalar(
            select(func.coalesce(func.sum(CreditEntry.quantity), 0)).where(
                CreditEntry.client_id == client_id
            )
        )
        assert Decimal(str(balance)) == Decimal(str(c["saldo"])), c["nombre"]


async def test_sale_totals_match_items(session: AsyncSession) -> None:
    data = _load_data()
    await seed(session, data)
    for v in data["VENTAS_DEMO"]:
        expected = sum(Decimal(str(i["precioUnitario"])) * i["cantidad"] for i in v["items"])
        total = await session.scalar(select(Sale.total).where(Sale.folio == v["folio"]))
        assert Decimal(str(total)) == expected, v["folio"]


async def test_force_wipe_preserves_real_identity(session: AsyncSession) -> None:
    await seed(session, _load_data())
    branch = await session.scalar(select(Branch).where(Branch.code == "T01"))
    user = UserProfile(
        email="real@example.com",
        full_name="Usuario real",
        role=Role.VENDEDOR,
    )
    session.add(user)
    await session.flush()
    user_id = user.id
    session.add(UserBranchAssignment(user_id=user.id, branch_id=branch.id))
    await session.flush()

    await _wipe(session)
    await seed(session, _load_data())
    await session.commit()

    assert await session.get(UserProfile, user_id) is not None
    assignments = await session.scalar(
        select(func.count())
        .select_from(UserBranchAssignment)
        .where(UserBranchAssignment.user_id == user_id)
    )
    assert assignments == 1
