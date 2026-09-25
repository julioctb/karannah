"""Seed de datos demo para la joyería.

Uso:
    python -m app.seed            # siembra o valida que el dataset este completo
    python -m app.seed --force    # reemplaza solo datos demo; preserva usuarios

El seed no crea identidades. Los usuarios internos se invitan con
`python -m app.provision_user`, usando el UUID emitido por Supabase Auth.

Las ventas históricas NO generan movimientos de inventario; el stock demo
se siembra como una entrada INICIAL por producto en la sucursal T01
(snapshot actual). El saldo de crédito de cada cliente se reconstruye con
entradas VENTA_CREDITO por venta a crédito + un AJUSTE por la diferencia
hasta el saldo demo.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, func, select

from app.auth_local import sync_local_users
from app.core.config import get_settings
from app.core.db import dispose_engine, get_session_factory
from app.models.cash import CashMovement, CashSession, Terminal
from app.models.catalog import (
    Category,
    Collection,
    Material,
    Product,
    ProductCollection,
    ProductGroup,
    ProductStatus,
    ProductVariant,
    SkuCounter,
    Subcategory,
)
from app.models.clients import Client, ClientType, CreditEntry, CreditMovementType
from app.models.identity import Branch
from app.models.inventory import StockBalance, StockEntry, StockMovementType
from app.models.repairs import Repair, RepairStatus
from app.models.sales import (
    DiscountApproval,
    FolioCounter,
    IdempotencyRecord,
    Payment,
    PaymentMethod,
    Sale,
    SaleCondition,
    SaleItem,
    SaleType,
)
from app.services.product_images import build_product_image_service

DATA_PATH = Path(__file__).with_name("seed_data.json")

BRANCH_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "joyeria-demo:branches")
STOCK_BASELINE = datetime(2026, 7, 31, 18, 0, tzinfo=UTC)


def _branch_id(code: str) -> uuid.UUID:
    return uuid.uuid5(BRANCH_NAMESPACE, code)


def _parse_dt(fecha: str, hora: str) -> datetime:
    return datetime.fromisoformat(f"{fecha}T{hora}").replace(tzinfo=UTC)


# Orden hijo -> padre para --force. Identidad y sucursales se preservan.
_DELETE_ORDER = (
    CashMovement,
    Payment,
    IdempotencyRecord,
    CreditEntry,
    SaleItem,
    Sale,
    DiscountApproval,
    CashSession,
    Terminal,
    FolioCounter,
    StockBalance,
    StockEntry,
    Repair,
    ProductCollection,
    ProductVariant,
    SkuCounter,
    Product,
    Collection,
    Subcategory,
    Material,
    Category,
    Client,
)


async def _wipe(session) -> None:  # type: ignore[no-untyped-def]
    for model in _DELETE_ORDER:
        await session.execute(delete(model))
    await session.flush()


async def seed(session, data: dict) -> None:  # type: ignore[no-untyped-def]
    # --- Sucursales -----------------------------------------------------
    existing_branches = {branch.code: branch for branch in await session.scalars(select(Branch))}
    branches: dict[str, Branch] = {}
    for s in data["SUCURSALES"]:
        branch = existing_branches.get(s["id"])
        if branch is None:
            branch = Branch(id=_branch_id(s["id"]), code=s["id"], name=s["nombre"])
            session.add(branch)
        else:
            branch.name = s["nombre"]
            branch.active = True
        branches[s["id"]] = branch
    await session.flush()
    existing_terminals = {
        terminal.branch_id: terminal for terminal in await session.scalars(select(Terminal))
    }
    for branch in branches.values():
        if branch.id not in existing_terminals:
            session.add(
                Terminal(
                    branch_id=branch.id,
                    code="POS-01",
                    name=f"Caja principal {branch.code}",
                )
            )

    # --- Catálogos --------------------------------------------------------
    categories: dict[str, Category] = {}
    for c in data["CATEGORIAS"]:
        group = ProductGroup(c["grupo"])
        category = Category(
            code=c["clave"],
            name=c["nombre"],
            group=group,
            requires_material=group is ProductGroup.JOYERIA,
        )
        categories[c["clave"]] = category
        session.add(category)

    materials: dict[str, Material] = {}
    for m in data["MATERIALES"]:
        material = Material(code=m["clave"], name=m["nombre"])
        materials[m["clave"]] = material
        session.add(material)
    await session.flush()

    subcategory_by_name: dict[tuple[str, str], Subcategory] = {}
    for cat_code, subs in data["SUBCATEGORIAS_SEED"].items():
        category = categories[cat_code]
        for sub in subs:
            row = Subcategory(
                category_id=category.id,
                name=sub["nombre"],
                active=sub["activa"],
                is_system=bool(sub.get("sistema", False)),
            )
            subcategory_by_name[(cat_code, sub["nombre"])] = row
            session.add(row)

    collections: dict[int, Collection] = {}
    for col in data["COLECCIONES_SEED"]:
        collection = Collection(name=col["nombre"], active=col["activa"])
        collections[col["id"]] = collection
        session.add(collection)
    # Los modelos no declaran relationships; cada capa FK se persiste por separado.
    await session.flush()

    # --- Productos ------------------------------------------------------------
    products_by_sku: dict[str, Product] = {}
    variants_by_sku: dict[str, ProductVariant] = {}
    for p in data["PRODUCTOS"]:
        sub_id = None
        if p["subcategoria"]:
            subcategory = subcategory_by_name.get((p["categoria"], p["subcategoria"]))
            sub_id = subcategory.id if subcategory else None
        product = Product(
            name=p["nombre"],
            category_id=categories[p["categoria"]].id,
            material_id=materials[p["material"]].id if p.get("material") else None,
            subcategory_id=sub_id,
            stone=p["piedra"],
            status=ProductStatus(p["estado"]),
        )
        products_by_sku[p["sku"]] = product
        session.add(product)
        await session.flush()
        variant = ProductVariant(
            product_id=product.id,
            sku=p["sku"],
            cost_price=Decimal(str(p["precio_costo"])),
            retail_price=Decimal(str(p["precio_menudeo"])),
            wholesale_price=Decimal(str(p["precio_mayoreo"])),
        )
        variants_by_sku[p["sku"]] = variant
        session.add(variant)
    await session.flush()

    for code, category in categories.items():
        suffixes = [
            int(p["sku"].rsplit("-", 1)[-1]) for p in data["PRODUCTOS"] if p["categoria"] == code
        ]
        session.add(SkuCounter(category_id=category.id, next_value=max(suffixes, default=0) + 1))

    for p in data["PRODUCTOS"]:
        for col_id in p.get("colecciones", []):
            session.add(
                ProductCollection(
                    product_id=products_by_sku[p["sku"]].id,
                    collection_id=collections[col_id].id,
                )
            )
    await session.flush()

    # --- Inventario (snapshot INICIAL en T01) ---------------------------------
    t01 = branches["T01"]
    for p in data["PRODUCTOS"]:
        if p["stock"]:
            variant = variants_by_sku[p["sku"]]
            session.add(
                StockEntry(
                    variant_id=variant.id,
                    branch_id=t01.id,
                    quantity=p["stock"],
                    movement_type=StockMovementType.INICIAL,
                    reference="SEED-DEMO",
                    note="Stock inicial demo",
                    created_by=None,
                    created_at=STOCK_BASELINE,
                )
            )
            session.add(
                StockBalance(
                    variant_id=variant.id,
                    branch_id=t01.id,
                    quantity=p["stock"],
                )
            )

    # --- Clientas y crédito -----------------------------------------------------
    clients_by_name: dict[str, Client] = {}
    for c in data["CLIENTES"]:
        client = Client(
            name=c["nombre"],
            type=ClientType(c["tipo"]),
            phone=c["telefono"],
            email=c["email"],
            credit_limit=Decimal(str(c["limiteCredito"])) if c["limiteCredito"] else None,
        )
        clients_by_name[c["nombre"]] = client
        session.add(client)
    await session.flush()

    # --- Ventas -------------------------------------------------------------------
    credit_debt: dict[int, Decimal] = {c.id: Decimal(0) for c in clients_by_name.values()}
    last_sale_dt = STOCK_BASELINE
    for v in data["VENTAS_DEMO"]:
        created_at = _parse_dt(v["fecha"], v["hora"])
        last_sale_dt = max(last_sale_dt, created_at)
        client = clients_by_name.get(v["cliente"])  # "Público general" → None
        branch = next(b for b in branches.values() if b.name == v["sucursal"])
        total = sum(
            (Decimal(str(i["precioUnitario"])) * i["cantidad"] for i in v["items"]),
            Decimal(0),
        )
        sale = Sale(
            folio=v["folio"],
            branch_id=branch.id,
            user_id=None,
            client_id=client.id if client else None,
            sale_type=SaleType(v["tipoVenta"]),
            condition=SaleCondition(v["condicion"]),
            payment_method=PaymentMethod(v["tipoPago"]),
            subtotal=(total / Decimal("1.16")).quantize(Decimal("0.01")),
            tax=total - (total / Decimal("1.16")).quantize(Decimal("0.01")),
            total=total,
            created_at=created_at,
        )
        session.add(sale)
        await session.flush()
        for item in v["items"]:
            variant = variants_by_sku[item["sku"]]
            product = products_by_sku[item["sku"]]
            line_total = Decimal(str(item["precioUnitario"])) * item["cantidad"]
            line_subtotal = (line_total / Decimal("1.16")).quantize(Decimal("0.01"))
            session.add(
                SaleItem(
                    sale_id=sale.id,
                    variant_id=variant.id,
                    sku=variant.sku,
                    product_name=product.name,
                    variant_value=variant.variant_value,
                    quantity=item["cantidad"],
                    unit_price=Decimal(str(item["precioUnitario"])),
                    base=line_total,
                    subtotal=line_subtotal,
                    tax=line_total - line_subtotal,
                    total=line_total,
                )
            )
        session.add(
            Payment(
                sale_id=sale.id,
                method=PaymentMethod(v["tipoPago"]),
                amount=total,
            )
        )
        if sale.condition is SaleCondition.CREDITO and client is not None:
            credit_debt[client.id] += total
            session.add(
                CreditEntry(
                    client_id=client.id,
                    branch_id=branch.id,
                    quantity=total,
                    movement_type=CreditMovementType.VENTA_CREDITO,
                    reference=sale.folio,
                    sale_id=sale.id,
                    payment_method=PaymentMethod.CREDITO.value,
                    created_by=sale.user_id,
                    created_at=created_at,
                )
            )

    # AJUSTE por diferencia entre saldo demo y deuda por ventas a crédito
    ajuste_at = last_sale_dt + timedelta(minutes=1)
    for c_data in data["CLIENTES"]:
        c = clients_by_name[c_data["nombre"]]
        delta = Decimal(str(c_data["saldo"])) - credit_debt[c.id]
        if delta:
            session.add(
                CreditEntry(
                    client_id=c.id,
                    quantity=delta,
                    movement_type=CreditMovementType.AJUSTE,
                    reference="SEED-DEMO",
                    note="Ajuste de saldo inicial demo",
                    created_by=None,
                    created_at=ajuste_at,
                )
            )

    # --- Reparaciones -------------------------------------------------------------
    for r in data["REPARACIONES"]:
        client = clients_by_name.get(r["cliente"])  # coincidencia exacta o texto libre
        session.add(
            Repair(
                folio=f"R-{r['id']:04d}",
                client_id=client.id if client else None,
                client_name=r["cliente"],
                product_description=r["producto"],
                service=r["servicio"],
                status=RepairStatus(r["estado"]),
                received_at=datetime.fromisoformat(r["fecha"]).date(),
                expected_at=(
                    datetime.fromisoformat(r["estimada"]).date() if r.get("estimada") else None
                ),
            )
        )


def _load_data() -> dict:  # type: ignore[type-arg]
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


async def _domain_seed_state(session, data: dict) -> str:  # type: ignore[no-untyped-def]
    expected = {
        Category: len(data["CATEGORIAS"]),
        Material: len(data["MATERIALES"]),
        Subcategory: sum(len(rows) for rows in data["SUBCATEGORIAS_SEED"].values()),
        Collection: len(data["COLECCIONES_SEED"]),
        Product: len(data["PRODUCTOS"]),
        ProductVariant: len(data["PRODUCTOS"]),
        SkuCounter: len(data["CATEGORIAS"]),
        Client: len(data["CLIENTES"]),
        Sale: len(data["VENTAS_DEMO"]),
        Repair: len(data["REPARACIONES"]),
    }
    counts = {
        model: await session.scalar(select(func.count()).select_from(model)) or 0
        for model in expected
    }
    if not any(counts.values()):
        return "empty"
    if all(counts[model] == count for model, count in expected.items()):
        return "complete"
    return "partial"


async def main(force: bool) -> None:
    data = _load_data()
    factory = get_session_factory()
    settings = get_settings()
    is_local = settings.auth_provider == "local"
    retained_image_keys: set[str] = set()
    try:
        async with factory() as session:
            state = await _domain_seed_state(session, data)
            if not force and state == "complete":
                if is_local:
                    await sync_local_users(session)
                    await session.commit()
                print("El dataset demo ya esta completo.")
                return
            if not force and state == "partial":
                raise RuntimeError("La base contiene un seed parcial; revisa o usa --force")
            if force:
                await _wipe(session)
            await seed(session, data)
            if is_local:
                await sync_local_users(session)
            if force:
                retained_image_keys = set(
                    await session.scalars(
                        select(Product.image_key).where(Product.image_key.is_not(None))
                    )
                )
            await session.commit()
        if force:
            build_product_image_service(settings).delete_unreferenced(retained_image_keys)
        print("Seed completado. Los usuarios reales se crean con app.provision_user.")
    finally:
        await dispose_engine()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Siembra datos demo")
    parser.add_argument("--force", action="store_true", help="Borra todo y re-siembra")
    args = parser.parse_args()
    asyncio.run(main(args.force))
