from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_claims
from app.api.v1.sales import _day_bounds
from app.core.db import Base, get_db
from app.core.security import TokenClaims
from app.main import app
from app.models.cash import Terminal
from app.models.catalog import (
    Category,
    Collection,
    Material,
    Product,
    ProductGroup,
    ProductStatus,
    ProductVariant,
    SkuCounter,
    Subcategory,
)
from app.models.clients import Client, ClientType, CreditEntry, CreditMovementType
from app.models.identity import Branch, Role, UserBranchAssignment, UserProfile
from app.models.inventory import StockBalance, StockEntry, StockMovementType
from app.models.repairs import Repair, RepairStatus
from app.models.sales import PaymentMethod, Sale, SaleCondition, SaleType
from app.services.pos import stock_balance_lock_statement

ADMIN_ID = uuid.uuid4()
VENDEDOR_ID = uuid.uuid4()
ENCARGADO_ID = uuid.uuid4()

BRANCH_IDS = {"T01": uuid.uuid4(), "T02": uuid.uuid4(), "A01": uuid.uuid4()}


@pytest_asyncio.fixture()
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        branches = {c: Branch(id=i, code=c, name=f"Suc {c}") for c, i in BRANCH_IDS.items()}
        admin = UserProfile(
            id=ADMIN_ID, email="admin@joyeria.com", full_name="Admin", role=Role.ADMIN
        )
        vendedor = UserProfile(
            id=VENDEDOR_ID,
            email="vendedor@joyeria.com",
            full_name="Vendedora T01",
            role=Role.VENDEDOR,
        )
        encargado = UserProfile(
            id=ENCARGADO_ID,
            email="encargado@joyeria.com",
            full_name="Encargada T01",
            role=Role.ENCARGADO,
        )
        s.add_all([*branches.values(), admin, vendedor, encargado])
        await s.flush()
        s.add_all(
            [
                UserBranchAssignment(user_id=VENDEDOR_ID, branch_id=BRANCH_IDS["T01"]),
                UserBranchAssignment(user_id=ENCARGADO_ID, branch_id=BRANCH_IDS["T01"]),
            ]
        )

        joyeria = Category(
            id=1, code="AN", name="Anillos", group=ProductGroup.JOYERIA, requires_material=True
        )
        bisuteria = Category(id=2, code="BI", name="Bisutería", group=ProductGroup.NO_JOYERIA)
        oro = Material(id=1, code="OR", name="Oro 14k")
        plata = Material(id=2, code="PL", name="Plata 925")
        s.add_all([joyeria, bisuteria, oro, plata])
        await s.flush()
        s.add_all(
            [
                Subcategory(id=1, category_id=1, name="Solitarios"),
                Subcategory(id=2, category_id=1, name="Alianzas"),
                Subcategory(id=3, category_id=2, name="Pulseras", active=False),
                Collection(id=1, name="Luna de Miel"),
                Collection(id=2, name="Fiesta 2024", active=False),
            ]
        )
        s.add_all(
            [
                *[
                    Terminal(
                        id=uuid.uuid5(uuid.NAMESPACE_URL, f"test-terminal:{code}"),
                        branch_id=branch_id,
                        code="POS-01",
                        name=f"Caja {code}",
                    )
                    for code, branch_id in BRANCH_IDS.items()
                ],
            ]
        )
        s.add_all(
            [
                Product(
                    id=1,
                    name="Anillo Solitario",
                    category_id=1,
                    material_id=1,
                    subcategory_id=1,
                    stone="Diamante",
                    status=ProductStatus.DISPONIBLE,
                ),
                Product(
                    id=2,
                    name="Pulsera Perlas",
                    category_id=2,
                    material_id=None,
                    subcategory_id=None,
                    stone=None,
                    status=ProductStatus.EXTERNO,
                ),
            ]
        )
        await s.flush()
        s.add_all(
            [
                ProductVariant(
                    id=1,
                    product_id=1,
                    sku="AN-001",
                    cost_price=1000.0,
                    retail_price=1800.0,
                    wholesale_price=1500.0,
                ),
                ProductVariant(
                    id=2,
                    product_id=2,
                    sku="BI-001",
                    cost_price=50.0,
                    retail_price=120.0,
                    wholesale_price=90.0,
                ),
                SkuCounter(category_id=1, next_value=2),
                SkuCounter(category_id=2, next_value=2),
            ]
        )
        s.add_all(
            [
                StockBalance(branch_id=BRANCH_IDS["T01"], variant_id=1, quantity=3),
                StockBalance(branch_id=BRANCH_IDS["T02"], variant_id=1, quantity=4),
                StockBalance(branch_id=BRANCH_IDS["A01"], variant_id=2, quantity=10),
                StockEntry(
                    variant_id=1,
                    branch_id=BRANCH_IDS["T01"],
                    quantity=5,
                    movement_type=StockMovementType.INICIAL,
                ),
                StockEntry(
                    variant_id=1,
                    branch_id=BRANCH_IDS["T01"],
                    quantity=-2,
                    movement_type=StockMovementType.VENTA,
                    reference="V-001",
                ),
                StockEntry(
                    variant_id=1,
                    branch_id=BRANCH_IDS["T02"],
                    quantity=4,
                    movement_type=StockMovementType.INICIAL,
                ),
                StockEntry(
                    variant_id=2,
                    branch_id=BRANCH_IDS["A01"],
                    quantity=10,
                    movement_type=StockMovementType.INICIAL,
                ),
            ]
        )

        maria = Client(
            id=1,
            name="María López",
            type=ClientType.MAYOREO,
            phone="5551112233",
            credit_limit=5000.0,
        )
        distribuidora = Client(
            id=2,
            name="Distribuidora SA",
            type=ClientType.MAYOREO,
            phone="5554445566",
            credit_limit=50000.0,
        )
        s.add_all([maria, distribuidora])
        await s.flush()
        s.add_all(
            [
                CreditEntry(
                    client_id=1,
                    quantity=100.0,
                    movement_type=CreditMovementType.VENTA_CREDITO,
                    reference="V-001",
                ),
                CreditEntry(
                    client_id=1,
                    quantity=-40.0,
                    movement_type=CreditMovementType.ABONO,
                ),
            ]
        )
        s.add_all(
            [
                Sale(
                    id=1,
                    folio="V-001",
                    branch_id=BRANCH_IDS["T01"],
                    client_id=1,
                    sale_type=SaleType.MENUDEO,
                    condition=SaleCondition.CREDITO,
                    payment_method=PaymentMethod.CREDITO,
                    total=1800.0,
                    created_at=datetime(2025, 3, 10, 12, 0, tzinfo=UTC),
                ),
                Sale(
                    id=2,
                    folio="V-002",
                    branch_id=BRANCH_IDS["T02"],
                    client_id=None,
                    sale_type=SaleType.MENUDEO,
                    condition=SaleCondition.CONTADO,
                    payment_method=PaymentMethod.EFECTIVO,
                    total=120.0,
                    created_at=datetime(2025, 3, 15, 15, 30, tzinfo=UTC),
                ),
                Sale(
                    id=3,
                    folio="V-003",
                    branch_id=BRANCH_IDS["T01"],
                    client_id=2,
                    sale_type=SaleType.MAYOREO,
                    condition=SaleCondition.CONTADO,
                    payment_method=PaymentMethod.TRANSFERENCIA,
                    total=900.0,
                    created_at=datetime(2025, 4, 2, 11, 0, tzinfo=UTC),
                ),
            ]
        )
        s.add_all(
            [
                Repair(
                    id=1,
                    folio="R-001",
                    client_id=1,
                    client_name="María López",
                    product_description="Anillo roto",
                    service="Soldadura",
                    status=RepairStatus.RECEIVED,
                    price=150.0,
                    received_at=date(2025, 3, 1),
                ),
                Repair(
                    id=2,
                    folio="R-002",
                    client_id=None,
                    client_name="Mostrador",
                    product_description="Cadena cortada",
                    service="Reparación",
                    status=RepairStatus.IN_WORKSHOP,
                    received_at=date(2025, 3, 20),
                ),
            ]
        )
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


def as_vendedor():
    return TokenClaims(user_id=str(VENDEDOR_ID), email="vendedor@joyeria.com", role="vendedor")


def as_encargado():
    return TokenClaims(user_id=str(ENCARGADO_ID), email="encargado@joyeria.com", role="encargado")


# ---------- catálogo ----------


async def test_catalog_reference_lists(client):
    cats = (await client.get("/api/v1/catalog/categories")).json()
    assert [c["code"] for c in cats] == ["AN", "BI"]
    mats = (await client.get("/api/v1/catalog/materials")).json()
    assert [m["name"] for m in mats] == ["Oro 14k", "Plata 925"]


async def test_subcategories_filters_inactive_by_default(client):
    subs = (await client.get("/api/v1/catalog/subcategories")).json()
    assert {s["id"] for s in subs} == {1, 2}
    subs_all = (
        await client.get("/api/v1/catalog/subcategories", params={"include_inactive": True})
    ).json()
    assert {s["id"] for s in subs_all} == {1, 2, 3}
    only_an = (await client.get("/api/v1/catalog/subcategories", params={"category_id": 1})).json()
    assert {s["id"] for s in only_an} == {1, 2}


async def test_collections_filters_inactive(client):
    cols = (await client.get("/api/v1/catalog/collections")).json()
    assert [c["name"] for c in cols] == ["Luna de Miel"]


async def test_products_admin_sees_cost(client):
    resp = await client.get("/api/v1/catalog/products")
    assert resp.status_code == 200
    items = resp.json()
    assert [p["sku"] for p in items] == ["AN-001", "BI-001"]
    anillo = items[0]
    assert anillo["category_name"] == "Anillos"
    assert anillo["material_name"] == "Oro 14k"
    assert anillo["subcategory_name"] == "Solitarios"
    assert float(anillo["cost_price"]) == 1000.0


async def test_products_vendedor_hides_cost(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    items = (await client.get("/api/v1/catalog/products")).json()
    assert all(p["cost_price"] is None for p in items)
    assert float(items[0]["retail_price"]) == 1800.0


async def test_products_search_and_filters(client):
    by_search = (await client.get("/api/v1/catalog/products", params={"search": "anillo"})).json()
    assert [p["sku"] for p in by_search] == ["AN-001"]
    by_status = (await client.get("/api/v1/catalog/products", params={"status": "externo"})).json()
    assert [p["sku"] for p in by_status] == ["BI-001"]
    by_cat = (await client.get("/api/v1/catalog/products", params={"category_id": 1})).json()
    assert [p["sku"] for p in by_cat] == ["AN-001"]
    by_mat = (await client.get("/api/v1/catalog/products", params={"material_id": 2})).json()
    assert [p["sku"] for p in by_mat] == []


async def test_admin_creates_catalog_product_and_variants_with_sequential_skus(client):
    subcategory = await client.post(
        "/api/v1/catalog/subcategories", json={"category_id": 1, "name": "Medias alianzas"}
    )
    assert subcategory.status_code == 201
    collection = await client.post("/api/v1/catalog/collections", json={"name": "Edición limitada"})
    assert collection.status_code == 201

    response = await client.post(
        "/api/v1/catalog/products",
        json={
            "name": "Anillo con variantes",
            "category_id": 1,
            "material_id": 1,
            "subcategory_id": subcategory.json()["id"],
            "stone": "Zafiro",
            "status": "disponible",
            "variant_type": "Talla",
            "collection_ids": [collection.json()["id"]],
            "variants": [
                {
                    "variant_value": "6",
                    "cost_price": "500.00",
                    "retail_price": "900.00",
                    "wholesale_price": "800.00",
                },
                {
                    "variant_value": "7",
                    "cost_price": "510.00",
                    "retail_price": "920.00",
                    "wholesale_price": "810.00",
                },
            ],
        },
    )

    assert response.status_code == 201
    product = response.json()
    assert [variant["sku"] for variant in product["variants"]] == [
        "AN-OR-0002",
        "AN-OR-0003",
    ]
    assert product["collection_ids"] == [collection.json()["id"]]

    added = await client.post(
        f"/api/v1/catalog/products/{product['id']}/variants",
        json={
            "variant_value": "8",
            "cost_price": "520.00",
            "retail_price": "940.00",
            "wholesale_price": "820.00",
        },
    )
    assert added.status_code == 201
    assert added.json()["variants"][-1]["sku"] == "AN-OR-0004"


async def test_vendedor_cannot_write_catalog(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    response = await client.post("/api/v1/catalog/collections", json={"name": "No autorizada"})
    assert response.status_code == 403


async def test_duplicate_category_code_returns_conflict(client):
    response = await client.post(
        "/api/v1/catalog/categories",
        json={
            "code": "AN",
            "name": "Otra categoría",
            "group": "joyeria",
            "requires_material": True,
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "La clave de categoria ya existe"


async def test_product_keeps_active_variant_and_reactivation_restores_variants(client):
    created = await client.post(
        "/api/v1/catalog/products",
        json={
            "name": "Anillo de prueba",
            "category_id": 1,
            "material_id": 1,
            "variant_type": "Talla",
            "variants": [
                {
                    "variant_value": "6",
                    "cost_price": "500.00",
                    "retail_price": "900.00",
                    "wholesale_price": "800.00",
                },
                {
                    "variant_value": "7",
                    "cost_price": "500.00",
                    "retail_price": "900.00",
                    "wholesale_price": "800.00",
                },
            ],
        },
    )
    assert created.status_code == 201
    product = created.json()
    first, second = product["variants"]

    disabled = await client.patch(
        f"/api/v1/catalog/products/{product['id']}/variants/{first['id']}",
        json={"active": False},
    )
    assert disabled.status_code == 200
    rejected = await client.patch(
        f"/api/v1/catalog/products/{product['id']}/variants/{second['id']}",
        json={"active": False},
    )
    assert rejected.status_code == 409

    deactivated = await client.delete(f"/api/v1/catalog/products/{product['id']}")
    assert deactivated.status_code == 204
    reactivated = await client.patch(
        f"/api/v1/catalog/products/{product['id']}", json={"active": True}
    )
    assert reactivated.status_code == 200
    assert all(variant["active"] for variant in reactivated.json()["variants"])


# ---------- inventario ----------


async def test_stock_admin_sees_all_branches_with_sums(client):
    rows = (await client.get("/api/v1/inventory/stock")).json()
    by_key = {(r["sku"], r["branch_code"]): r["quantity"] for r in rows}
    assert by_key == {("AN-001", "T01"): 3, ("AN-001", "T02"): 4, ("BI-001", "A01"): 10}


async def test_stock_vendedor_only_t01(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    rows = (await client.get("/api/v1/inventory/stock")).json()
    assert {(r["sku"], r["branch_code"], r["quantity"]) for r in rows} == {("AN-001", "T01", 3)}


async def test_stock_branch_outside_scope_is_empty(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    rows = (
        await client.get("/api/v1/inventory/stock", params={"branch_id": str(BRANCH_IDS["T02"])})
    ).json()
    assert rows == []


async def test_stock_search(client):
    rows = (await client.get("/api/v1/inventory/stock", params={"search": "pulsera"})).json()
    assert [(r["sku"], r["branch_code"]) for r in rows] == [("BI-001", "A01")]


async def test_inventory_adjustment_appends_movement_and_rejects_negative_balance(client):
    response = await client.post(
        "/api/v1/inventory/adjustments",
        json={
            "variant_id": 1,
            "branch_id": str(BRANCH_IDS["T01"]),
            "quantity": 2,
            "reference": "CONTEO-1",
            "note": "Diferencia confirmada en conteo",
        },
    )
    assert response.status_code == 201
    assert response.json()["resulting_quantity"] == 5

    stock = (
        await client.get("/api/v1/inventory/stock", params={"branch_id": str(BRANCH_IDS["T01"])})
    ).json()
    assert stock[0]["quantity"] == 5
    movements = (
        await client.get(
            "/api/v1/inventory/movements",
            params={"branch_id": str(BRANCH_IDS["T01"]), "variant_id": 1},
        )
    ).json()
    assert len(movements) == 3
    adjustment = next(item for item in movements if item["reference"] == "CONTEO-1")
    assert adjustment["movement_type"] == "ajuste"
    assert adjustment["quantity"] == 2

    rejected = await client.post(
        "/api/v1/inventory/adjustments",
        json={
            "variant_id": 1,
            "branch_id": str(BRANCH_IDS["T01"]),
            "quantity": -6,
            "note": "No debe permitir saldo negativo",
        },
    )
    assert rejected.status_code == 409


async def test_vendedor_cannot_adjust_inventory(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    response = await client.post(
        "/api/v1/inventory/adjustments",
        json={
            "variant_id": 1,
            "branch_id": str(BRANCH_IDS["T01"]),
            "quantity": 1,
            "note": "Intento no autorizado",
        },
    )
    assert response.status_code == 403


# ---------- clientes ----------


async def test_clients_credit_balance_derived(client):
    rows = (await client.get("/api/v1/clients")).json()
    by_name = {c["name"]: c for c in rows}
    assert float(by_name["María López"]["credit_balance"]) == 60.0
    assert float(by_name["Distribuidora SA"]["credit_balance"]) == 0.0


async def test_clients_search_and_type_filter(client):
    found = (await client.get("/api/v1/clients", params={"search": "maría"})).json()
    assert [c["name"] for c in found] == ["María López"]
    mayoreo = (await client.get("/api/v1/clients", params={"type": "mayoreo"})).json()
    assert [c["name"] for c in mayoreo] == ["Distribuidora SA", "María López"]


async def test_client_creation_forces_retail_without_credit(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    response = await client.post(
        "/api/v1/clients",
        json={
            "name": "  Cliente Nuevo  ",
            "phone": "5550001122",
            "email": "NUEVO@EJEMPLO.COM",
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Cliente Nuevo"
    assert created["type"] == "menudeo"
    assert created["credit_limit"] is None
    assert float(created["credit_balance"]) == 0


async def test_only_admin_updates_client_commercial_profile(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    denied = await client.patch(
        "/api/v1/clients/1/commercial-profile",
        json={"type": "mayoreo", "credit_limit": "10000.00"},
    )
    assert denied.status_code == 403

    app.dependency_overrides[get_current_claims] = lambda: TokenClaims(
        user_id=str(ADMIN_ID), email="admin@joyeria.com", role="admin"
    )
    updated = await client.patch(
        "/api/v1/clients/1/commercial-profile",
        json={"type": "mayoreo", "credit_limit": "10000.00"},
    )
    assert updated.status_code == 200
    assert updated.json()["type"] == "mayoreo"
    assert float(updated.json()["credit_limit"]) == 10000


# ---------- ventas ----------


async def test_sales_admin_sees_all(client):
    rows = (await client.get("/api/v1/sales")).json()
    assert [r["folio"] for r in rows] == ["V-003", "V-002", "V-001"]  # created_at desc
    v1 = next(r for r in rows if r["folio"] == "V-001")
    assert v1["client_name"] == "María López"
    assert v1["branch_code"] == "T01"


async def test_sales_vendedor_scoped_to_branch(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    rows = (await client.get("/api/v1/sales")).json()
    assert {r["folio"] for r in rows} == {"V-001", "V-003"}
    assert all(r["branch_code"] == "T01" for r in rows)


async def test_sales_date_range_and_client_filter(client):
    rows = (
        await client.get(
            "/api/v1/sales", params={"date_from": "2025-03-11", "date_to": "2025-03-31"}
        )
    ).json()
    assert [r["folio"] for r in rows] == ["V-002"]
    by_client = (await client.get("/api/v1/sales", params={"client_id": 1})).json()
    assert [r["folio"] for r in by_client] == ["V-001"]


def test_sales_day_bounds_use_mexico_city_timezone():
    start, next_day = _day_bounds(date(2025, 3, 10))
    assert start.isoformat() == "2025-03-10T00:00:00-06:00"
    assert next_day.isoformat() == "2025-03-11T00:00:00-06:00"


# ---------- reparaciones ----------


async def test_repairs_list_and_status_filter(client):
    rows = (await client.get("/api/v1/repairs")).json()
    assert [r["folio"] for r in rows] == ["R-002", "R-001"]
    assert rows[1]["price"] == "150.00"
    assert "quoted_price" not in rows[1]
    received = (await client.get("/api/v1/repairs", params={"status": "received"})).json()
    assert [r["folio"] for r in received] == ["R-001"]


async def test_repairs_visible_to_vendedor(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    resp = await client.get("/api/v1/repairs")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ---------- paginación ----------


async def test_pagination_limit_offset(client):
    page1 = (await client.get("/api/v1/catalog/products", params={"limit": 1})).json()
    assert [p["sku"] for p in page1] == ["AN-001"]
    page2 = (await client.get("/api/v1/catalog/products", params={"limit": 1, "offset": 1})).json()
    assert [p["sku"] for p in page2] == ["BI-001"]
    bad = await client.get("/api/v1/catalog/products", params={"limit": 0})
    assert bad.status_code == 422
    bad = await client.get("/api/v1/catalog/products", params={"limit": 501})
    assert bad.status_code == 422


# ---------- POS fase 4 ----------


def _terminal_id(code: str = "T01") -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"test-terminal:{code}"))


def test_checkout_stock_query_uses_ordered_postgresql_row_locks():
    sql = str(
        stock_balance_lock_statement(BRANCH_IDS["T01"], [2, 1]).compile(
            dialect=postgresql.dialect()
        )
    )
    assert "ORDER BY stock_balances.variant_id" in sql
    assert sql.endswith("FOR UPDATE")


async def _open_t01(client, opening: str = "100.00") -> dict:
    response = await client.post(
        "/api/v1/cash/sessions/open",
        json={"terminal_id": _terminal_id(), "opening_amount": opening},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _checkout_payload(
    session_id: str,
    *,
    quantity: int = 1,
    discount: str = "0.00",
    method: str = "efectivo",
    amount: str = "1800.00",
    client_id: int | None = None,
    approval_id: str | None = None,
) -> dict:
    payload = {
        "branch_id": str(BRANCH_IDS["T01"]),
        "sale_type": "menudeo",
        "items": [{"variant_id": 1, "quantity": quantity}],
        "discount_percent": discount,
        "cash_session_id": session_id,
        "client_id": client_id,
        "payments": [{"method": method, "amount": amount}],
    }
    if approval_id:
        payload["discount_approval_id"] = approval_id
    return payload


async def test_quote_uses_catalog_price_stock_and_tax_inclusive_semantics(client):
    response = await client.post(
        "/api/v1/sales/quote",
        json={
            "branch_id": str(BRANCH_IDS["T01"]),
            "sale_type": "menudeo",
            "items": [{"variant_id": 1, "quantity": 1}],
            "discount_percent": "0.00",
        },
    )
    assert response.status_code == 200
    quote = response.json()
    assert quote["lines"][0]["unit_price"] == "1800.00"
    assert quote["lines"][0]["available_quantity"] == 3
    assert quote["base"] == "1800.00"
    assert quote["subtotal"] == "1551.72"
    assert quote["tax"] == "248.28"
    assert quote["total"] == "1800.00"

    attempted_client_price = await client.post(
        "/api/v1/sales/quote",
        json={
            "branch_id": str(BRANCH_IDS["T01"]),
            "items": [{"variant_id": 1, "quantity": 1, "unit_price": "1.00"}],
        },
    )
    assert attempted_client_price.status_code == 422


async def test_checkout_requires_open_cash_session_and_rolls_back(client):
    response = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "no-cash-session"},
        json=_checkout_payload(str(uuid.uuid4())),
    )
    assert response.status_code == 409
    stock = (await client.get("/api/v1/inventory/stock")).json()
    assert next(row for row in stock if row["branch_code"] == "T01")["quantity"] == 3
    assert len((await client.get("/api/v1/sales")).json()) == 3


async def test_checkout_is_atomic_detailed_and_idempotent(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    session = await _open_t01(client)
    payload = _checkout_payload(session["id"])

    bad_payment = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "bad-payment"},
        json={**payload, "payments": [{"method": "efectivo", "amount": "1799.99"}]},
    )
    assert bad_payment.status_code == 422
    stock = (await client.get("/api/v1/inventory/stock")).json()
    assert stock[0]["quantity"] == 3

    first = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "sale-atomic-1"},
        json=payload,
    )
    assert first.status_code == 201, first.text
    sale = first.json()
    assert sale["folio"].startswith("VTA-T01-")
    assert sale["items"][0]["sku"] == "AN-001"
    assert sale["items"][0]["product_name"] == "Anillo Solitario"
    assert sale["payments"] == [
        {
            "id": sale["payments"][0]["id"],
            "method": "efectivo",
            "amount": "1800.00",
            "cash_session_id": session["id"],
            "created_at": sale["payments"][0]["created_at"],
        }
    ]

    repeated = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "sale-atomic-1"},
        json=payload,
    )
    assert repeated.status_code == 201
    assert repeated.json() == sale
    different = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "sale-atomic-1"},
        json={**payload, "items": [{"variant_id": 1, "quantity": 2}]},
    )
    assert different.status_code == 409

    detail = await client.get(f"/api/v1/sales/{sale['id']}")
    assert detail.status_code == 200
    assert detail.json() == sale
    stock = (await client.get("/api/v1/inventory/stock")).json()
    assert stock[0]["quantity"] == 2
    current = await client.get(
        "/api/v1/cash/sessions/current", params={"terminal_id": _terminal_id()}
    )
    assert current.json()["expected_cash"] == "1900.00"


async def test_stock_and_credit_limits_are_rechecked_at_checkout(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    session = await _open_t01(client)
    over_credit = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "credit-over-limit"},
        json=_checkout_payload(
            session["id"],
            quantity=3,
            method="credito",
            amount="5400.00",
            client_id=1,
        ),
    )
    assert over_credit.status_code == 409
    assert "limite" in over_credit.json()["detail"]
    stock = (await client.get("/api/v1/inventory/stock")).json()
    assert stock[0]["quantity"] == 3

    sold = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "sell-two"},
        json=_checkout_payload(session["id"], quantity=2, amount="3600.00"),
    )
    assert sold.status_code == 201
    oversell = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "oversell"},
        json=_checkout_payload(session["id"], quantity=2, amount="3600.00"),
    )
    assert oversell.status_code == 409
    assert "Stock insuficiente" in oversell.json()["detail"]


async def test_checkout_rejects_credit_for_retail_client(client):
    retail = await client.post("/api/v1/clients", json={"name": "Cliente contado"})
    assert retail.status_code == 201
    session = await _open_t01(client)
    response = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "retail-credit"},
        json=_checkout_payload(
            session["id"],
            method="credito",
            amount="1800.00",
            client_id=retail.json()["id"],
        ),
    )
    assert response.status_code == 422
    assert "mayoreo" in response.json()["detail"]


async def test_discount_limit_requires_separate_authorized_approval(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    session = await _open_t01(client)
    discounted = _checkout_payload(session["id"], discount="5.00", amount="1710.00")
    denied = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "discount-denied"},
        json=discounted,
    )
    assert denied.status_code == 403

    app.dependency_overrides[get_current_claims] = as_encargado
    excessive = await client.post(
        "/api/v1/sales/discount-approvals",
        json={
            "branch_id": str(BRANCH_IDS["T01"]),
            "sale_type": "menudeo",
            "items": [{"variant_id": 1, "quantity": 1}],
            "discount_percent": "11.00",
        },
    )
    assert excessive.status_code == 403
    approval = await client.post(
        "/api/v1/sales/discount-approvals",
        json={
            "branch_id": str(BRANCH_IDS["T01"]),
            "sale_type": "menudeo",
            "items": [{"variant_id": 1, "quantity": 1}],
            "discount_percent": "5.00",
        },
    )
    assert approval.status_code == 201, approval.text

    app.dependency_overrides[get_current_claims] = as_vendedor
    approved = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "discount-approved"},
        json={**discounted, "discount_approval_id": approval.json()["id"]},
    )
    assert approved.status_code == 201, approved.text
    assert approved.json()["discount"] == "90.00"
    assert approved.json()["discount_approved_by"] == str(ENCARGADO_ID)
    consumed = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "discount-approved-again"},
        json={**discounted, "discount_approval_id": approval.json()["id"]},
    )
    assert consumed.status_code == 403


async def test_credit_ledger_is_paginated_and_exposes_branch_traceability(client):
    response = await client.get("/api/v1/clients/1/credit-ledger", params={"limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["movement_type"] in {"venta_credito", "abono"}

    remaining = await client.get(
        "/api/v1/clients/1/credit-ledger", params={"limit": 1, "offset": 1}
    )
    assert remaining.status_code == 200
    assert len(remaining.json()) == 1
    missing = await client.get("/api/v1/clients/999/credit-ledger")
    assert missing.status_code == 404


async def test_credit_recovery_report_returns_outstanding_balances_and_period_totals(client):
    response = await client.get("/api/v1/reports/credit-recovery")
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["total_clients"] == 1
    assert report["totals"] == {
        "clients_with_balance": 1,
        "current_balance": "60.00",
        "period_charged": "100.00",
        "period_recovered": "40.00",
        "period_net": "60.00",
    }
    assert report["rows"][0]["client_id"] == 1
    assert report["rows"][0]["period_net"] == "60.00"

    invalid_dates = await client.get(
        "/api/v1/reports/credit-recovery",
        params={"date_from": "2025-04-01", "date_to": "2025-03-01"},
    )
    assert invalid_dates.status_code == 422


async def test_sale_cancellation_reverses_stock_payment_cash_and_is_idempotent(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    session = await _open_t01(client)
    created = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "sale-to-cancel"},
        json=_checkout_payload(session["id"]),
    )
    assert created.status_code == 201, created.text
    sale_id = created.json()["id"]

    app.dependency_overrides[get_current_claims] = as_encargado
    cancelled = await client.post(
        f"/api/v1/sales/{sale_id}/cancel",
        headers={"Idempotency-Key": "cancel-sale-1"},
        json={"reason": "Solicitud del cliente"},
    )
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "cancelada"
    assert cancelled.json()["cancellation_reason"] == "Solicitud del cliente"
    assert sorted(payment["amount"] for payment in cancelled.json()["payments"]) == [
        "-1800.00",
        "1800.00",
    ]

    stock = (await client.get("/api/v1/inventory/stock")).json()
    assert next(row for row in stock if row["branch_code"] == "T01")["quantity"] == 3
    current = await client.get(
        "/api/v1/cash/sessions/current", params={"terminal_id": _terminal_id()}
    )
    assert current.json()["expected_cash"] == "100.00"

    repeated = await client.post(
        f"/api/v1/sales/{sale_id}/cancel",
        headers={"Idempotency-Key": "cancel-sale-1"},
        json={"reason": "Solicitud del cliente"},
    )
    assert repeated.status_code == 200
    assert repeated.json() == cancelled.json()
    different = await client.post(
        f"/api/v1/sales/{sale_id}/cancel",
        headers={"Idempotency-Key": "cancel-sale-2"},
        json={"reason": "Otro motivo"},
    )
    assert different.status_code == 409


async def test_branch_scope_cash_close_permissions_and_credit_cash_movement(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    outside = await client.post(
        "/api/v1/sales/quote",
        json={
            "branch_id": str(BRANCH_IDS["T02"]),
            "items": [{"variant_id": 1, "quantity": 1}],
        },
    )
    assert outside.status_code == 404
    assert [
        terminal["branch_code"] for terminal in (await client.get("/api/v1/cash/terminals")).json()
    ] == ["T01"]

    session = await _open_t01(client)
    payment = await client.post(
        "/api/v1/clients/1/credit-payments",
        headers={"Idempotency-Key": "credit-payment-1"},
        json={
            "branch_id": str(BRANCH_IDS["T01"]),
            "amount": "20.00",
            "method": "efectivo",
            "cash_session_id": session["id"],
        },
    )
    assert payment.status_code == 201, payment.text
    assert payment.json()["resulting_balance"] == "40.00"
    repeated_payment = await client.post(
        "/api/v1/clients/1/credit-payments",
        headers={"Idempotency-Key": "credit-payment-1"},
        json={
            "branch_id": str(BRANCH_IDS["T01"]),
            "amount": "20.00",
            "method": "efectivo",
            "cash_session_id": session["id"],
        },
    )
    assert repeated_payment.status_code == 201
    assert repeated_payment.json() == payment.json()
    changed_payment = await client.post(
        "/api/v1/clients/1/credit-payments",
        headers={"Idempotency-Key": "credit-payment-1"},
        json={
            "branch_id": str(BRANCH_IDS["T01"]),
            "amount": "10.00",
            "method": "efectivo",
            "cash_session_id": session["id"],
        },
    )
    assert changed_payment.status_code == 409
    current = await client.get(
        "/api/v1/cash/sessions/current", params={"terminal_id": _terminal_id()}
    )
    assert current.json()["expected_cash"] == "120.00"
    assert (
        await client.post(
            f"/api/v1/cash/sessions/{session['id']}/close", json={"counted_cash": "120.00"}
        )
    ).status_code == 403

    app.dependency_overrides[get_current_claims] = as_encargado
    closed = await client.post(
        f"/api/v1/cash/sessions/{session['id']}/close", json={"counted_cash": "119.00"}
    )
    assert closed.status_code == 200
    assert closed.json()["variance"] == "-1.00"

    app.dependency_overrides[get_current_claims] = as_vendedor
    hidden_detail = await client.get("/api/v1/sales/2")
    assert hidden_detail.status_code == 404
