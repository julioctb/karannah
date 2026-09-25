from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.cash import CashMovement, CashMovementType, CashSession, CashSessionStatus, Terminal
from app.models.catalog import Product, ProductVariant
from app.models.clients import Client, ClientType, CreditEntry, CreditMovementType
from app.models.identity import Branch, Role, UserProfile
from app.models.inventory import StockBalance, StockEntry, StockMovementType
from app.models.sales import (
    DiscountApproval,
    FolioCounter,
    IdempotencyRecord,
    Payment,
    PaymentMethod,
    Sale,
    SaleCondition,
    SaleItem,
    SaleStatus,
)
from app.schemas.sales import (
    CancelSaleCreate,
    CheckoutCreate,
    PaymentRead,
    QuoteCreate,
    QuoteLineRead,
    QuoteRead,
    SaleDetailRead,
    SaleItemRead,
)

CENT = Decimal("0.01")
IVA_RATE = Decimal("0.16")
DISCOUNT_LIMITS = {
    Role.VENDEDOR: Decimal(0),
    Role.ENCARGADO: Decimal(10),
    Role.ADMIN: Decimal(100),
}


def money(value: Decimal | int) -> Decimal:
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def request_hash(payload: BaseModel) -> str:
    raw = json.dumps(payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def quote_fingerprint(quote: QuoteRead) -> str:
    canonical = {
        "branch_id": str(quote.branch_id),
        "sale_type": quote.sale_type.value,
        "discount_percent": str(quote.discount_percent),
        "lines": [
            {
                "variant_id": line.variant_id,
                "quantity": line.quantity,
                "unit_price": str(line.unit_price),
                "base": str(line.base),
                "discount": str(line.discount),
                "total": str(line.total),
            }
            for line in quote.lines
        ],
    }
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def stock_balance_lock_statement(branch_id: uuid.UUID, variant_ids: list[int]):
    return (
        select(StockBalance)
        .where(
            StockBalance.branch_id == branch_id,
            StockBalance.variant_id.in_(variant_ids),
        )
        .order_by(StockBalance.variant_id)
        .with_for_update()
    )


async def build_quote(
    db: AsyncSession,
    payload: QuoteCreate,
    profile: UserProfile,
    *,
    lock_stock: bool = False,
) -> QuoteRead:
    variant_ids = [item.variant_id for item in payload.items]
    if lock_stock:
        await db.execute(stock_balance_lock_statement(payload.branch_id, variant_ids))

    rows = (
        await db.execute(
            select(
                ProductVariant.id,
                ProductVariant.sku,
                ProductVariant.variant_value,
                ProductVariant.retail_price,
                ProductVariant.wholesale_price,
                Product.name.label("product_name"),
                StockBalance.quantity.label("available_quantity"),
            )
            .join(Product, Product.id == ProductVariant.product_id)
            .outerjoin(
                StockBalance,
                (StockBalance.variant_id == ProductVariant.id)
                & (StockBalance.branch_id == payload.branch_id),
            )
            .where(
                ProductVariant.id.in_(variant_ids),
                ProductVariant.active.is_(True),
                Product.active.is_(True),
            )
        )
    ).mappings()
    by_id = {row["id"]: row for row in rows}
    lines: list[QuoteLineRead] = []
    for requested in payload.items:
        row = by_id.get(requested.variant_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Producto o variante no disponible")
        available = int(row["available_quantity"] or 0)
        if available < requested.quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Stock insuficiente para {row['sku']}: disponible {available}",
            )
        unit_price = money(
            row["wholesale_price"] if payload.sale_type.value == "mayoreo" else row["retail_price"]
        )
        base = money(unit_price * requested.quantity)
        discount = money(base * payload.discount_percent / Decimal(100))
        total = money(base - discount)
        tax = money(total * IVA_RATE / (Decimal(1) + IVA_RATE))
        subtotal = money(total - tax)
        lines.append(
            QuoteLineRead(
                variant_id=row["id"],
                sku=row["sku"],
                product_name=row["product_name"],
                variant_value=row["variant_value"],
                quantity=requested.quantity,
                available_quantity=available,
                unit_price=unit_price,
                base=base,
                discount=discount,
                subtotal=subtotal,
                tax=tax,
                total=total,
            )
        )
    base = money(sum((line.base for line in lines), Decimal(0)))
    discount = money(sum((line.discount for line in lines), Decimal(0)))
    subtotal = money(sum((line.subtotal for line in lines), Decimal(0)))
    tax = money(sum((line.tax for line in lines), Decimal(0)))
    total = money(sum((line.total for line in lines), Decimal(0)))
    result = QuoteRead(
        branch_id=payload.branch_id,
        sale_type=payload.sale_type,
        lines=lines,
        base=base,
        discount_percent=payload.discount_percent,
        discount=discount,
        subtotal=subtotal,
        tax=tax,
        total=total,
        approval_required=payload.discount_percent > DISCOUNT_LIMITS[profile.role],
        fingerprint="",
    )
    result.fingerprint = quote_fingerprint(result)
    return result


async def lock_open_cash_session(
    db: AsyncSession, session_id: uuid.UUID, branch_id: uuid.UUID
) -> CashSession:
    row = await db.scalar(select(CashSession).where(CashSession.id == session_id).with_for_update())
    if row is None or row.branch_id != branch_id or row.status is not CashSessionStatus.ABIERTA:
        raise HTTPException(status_code=409, detail="Se requiere una sesion de caja abierta")
    terminal = await db.get(Terminal, row.terminal_id)
    if terminal is None or not terminal.active:
        raise HTTPException(status_code=409, detail="La terminal de caja no esta activa")
    return row


async def expected_cash(db: AsyncSession, session: CashSession) -> Decimal:
    movements = await db.scalar(
        select(func.coalesce(func.sum(CashMovement.amount), 0)).where(
            CashMovement.cash_session_id == session.id
        )
    )
    return money(session.opening_amount + Decimal(movements or 0))


async def _idempotency_record(
    db: AsyncSession,
    profile: UserProfile,
    key: str,
    payload_hash: str,
    endpoint: str = "sales.checkout",
) -> IdempotencyRecord:
    dialect = db.get_bind().dialect.name
    if dialect == "postgresql":
        await db.execute(
            pg_insert(IdempotencyRecord)
            .values(
                id=uuid.uuid4(),
                user_id=profile.id,
                endpoint=endpoint,
                key=key,
                request_hash=payload_hash,
            )
            .on_conflict_do_nothing(index_elements=["user_id", "endpoint", "key"])
        )
    else:
        existing = await db.scalar(
            select(IdempotencyRecord).where(
                IdempotencyRecord.user_id == profile.id,
                IdempotencyRecord.endpoint == endpoint,
                IdempotencyRecord.key == key,
            )
        )
        if existing is None:
            db.add(
                IdempotencyRecord(
                    user_id=profile.id,
                    endpoint=endpoint,
                    key=key,
                    request_hash=payload_hash,
                )
            )
            await db.flush()
    record = await db.scalar(
        select(IdempotencyRecord)
        .where(
            IdempotencyRecord.user_id == profile.id,
            IdempotencyRecord.endpoint == endpoint,
            IdempotencyRecord.key == key,
        )
        .with_for_update()
    )
    assert record is not None
    if record.request_hash != payload_hash:
        raise HTTPException(
            status_code=409, detail="Idempotency-Key ya fue usado con otra solicitud"
        )
    return record


async def _next_folio(db: AsyncSession, branch: Branch) -> str:
    year = datetime.now(ZoneInfo(get_settings().business_timezone)).year
    key = {"document_type": "VTA", "branch_id": branch.id, "business_year": year}
    if db.get_bind().dialect.name == "postgresql":
        await db.execute(pg_insert(FolioCounter).values(**key).on_conflict_do_nothing())
    elif await db.get(FolioCounter, ("VTA", branch.id, year)) is None:
        db.add(FolioCounter(**key))
        await db.flush()
    counter = await db.scalar(select(FolioCounter).filter_by(**key).with_for_update())
    assert counter is not None
    number = counter.next_value
    counter.next_value += 1
    return f"VTA-{branch.code}-{year}-{number:06d}"


def _aware_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


async def _authorize_discount(
    db: AsyncSession,
    payload: CheckoutCreate,
    quote: QuoteRead,
    profile: UserProfile,
) -> DiscountApproval | None:
    if payload.discount_percent <= DISCOUNT_LIMITS[profile.role]:
        return None
    if payload.discount_approval_id is None:
        raise HTTPException(status_code=403, detail="El descuento requiere aprobacion")
    approval = await db.scalar(
        select(DiscountApproval)
        .where(DiscountApproval.id == payload.discount_approval_id)
        .with_for_update()
    )
    now = datetime.now(UTC)
    if (
        approval is None
        or approval.branch_id != payload.branch_id
        or approval.request_fingerprint != quote.fingerprint
        or approval.max_discount_percent < payload.discount_percent
        or approval.consumed_at is not None
        or _aware_utc(approval.expires_at) <= now
        or approval.approved_by == profile.id
    ):
        raise HTTPException(status_code=403, detail="Aprobacion de descuento invalida o vencida")
    approval.consumed_at = now
    return approval


async def checkout(
    db: AsyncSession,
    payload: CheckoutCreate,
    profile: UserProfile,
    branch: Branch,
    idempotency_key: str,
) -> SaleDetailRead:
    idem = await _idempotency_record(db, profile, idempotency_key, request_hash(payload))
    if idem.response is not None:
        return SaleDetailRead.model_validate(idem.response)

    cash_session = await lock_open_cash_session(db, payload.cash_session_id, payload.branch_id)
    quote = await build_quote(db, payload, profile, lock_stock=True)
    approval = await _authorize_discount(db, payload, quote, profile)

    payment_total = money(sum((payment.amount for payment in payload.payments), Decimal(0)))
    if payment_total != quote.total:
        raise HTTPException(status_code=422, detail="Los pagos deben sumar exactamente el total")
    credit_amount = money(
        sum(
            (
                payment.amount
                for payment in payload.payments
                if payment.method is PaymentMethod.CREDITO
            ),
            Decimal(0),
        )
    )
    client: Client | None = None
    if payload.client_id is not None:
        client = await db.scalar(
            select(Client).where(Client.id == payload.client_id).with_for_update()
        )
        if client is None or not client.active:
            raise HTTPException(status_code=404, detail="Cliente activo no encontrado")
    if credit_amount:
        if (
            client is None
            or client.type is not ClientType.MAYOREO
            or client.credit_limit is None
        ):
            raise HTTPException(
                status_code=422,
                detail="El credito requiere un cliente mayoreo con limite disponible",
            )
        balance = Decimal(
            await db.scalar(
                select(func.coalesce(func.sum(CreditEntry.quantity), 0)).where(
                    CreditEntry.client_id == client.id
                )
            )
            or 0
        )
        if money(balance + credit_amount) > client.credit_limit:
            raise HTTPException(status_code=409, detail="El credito excede el limite del cliente")

    folio = await _next_folio(db, branch)
    methods = {payment.method for payment in payload.payments}
    payment_method = next(iter(methods)) if len(methods) == 1 else PaymentMethod.MIXTO
    sale = Sale(
        folio=folio,
        branch_id=payload.branch_id,
        user_id=profile.id,
        client_id=client.id if client else None,
        cash_session_id=cash_session.id,
        sale_type=payload.sale_type,
        condition=SaleCondition.CREDITO if credit_amount else SaleCondition.CONTADO,
        payment_method=payment_method,
        subtotal=quote.subtotal,
        discount=quote.discount,
        discount_percent=quote.discount_percent,
        tax=quote.tax,
        total=quote.total,
        discount_approval_id=approval.id if approval else None,
        discount_approved_by=approval.approved_by if approval else None,
    )
    db.add(sale)
    await db.flush()

    for line in quote.lines:
        balance = await db.get(StockBalance, (payload.branch_id, line.variant_id))
        assert balance is not None
        balance.quantity -= line.quantity
        db.add(
            StockEntry(
                variant_id=line.variant_id,
                branch_id=payload.branch_id,
                quantity=-line.quantity,
                movement_type=StockMovementType.VENTA,
                reference=folio,
                created_by=profile.id,
            )
        )
        db.add(
            SaleItem(
                sale_id=sale.id,
                variant_id=line.variant_id,
                sku=line.sku,
                product_name=line.product_name,
                variant_value=line.variant_value,
                quantity=line.quantity,
                unit_price=line.unit_price,
                base=line.base,
                discount=line.discount,
                subtotal=line.subtotal,
                tax=line.tax,
                total=line.total,
            )
        )

    for submitted in payload.payments:
        payment = Payment(
            sale_id=sale.id,
            method=submitted.method,
            amount=money(submitted.amount),
            cash_session_id=(
                cash_session.id if submitted.method is PaymentMethod.EFECTIVO else None
            ),
        )
        db.add(payment)
        if submitted.method is PaymentMethod.EFECTIVO:
            db.add(
                CashMovement(
                    cash_session_id=cash_session.id,
                    movement_type=CashMovementType.VENTA,
                    amount=money(submitted.amount),
                    reference=folio,
                    created_by=profile.id,
                )
            )
    if credit_amount and client is not None:
        db.add(
            CreditEntry(
                client_id=client.id,
                branch_id=payload.branch_id,
                quantity=credit_amount,
                movement_type=CreditMovementType.VENTA_CREDITO,
                reference=folio,
                sale_id=sale.id,
                payment_method=PaymentMethod.CREDITO.value,
                created_by=profile.id,
            )
        )
    await db.flush()
    result = await sale_detail(db, sale.id)
    idem.response = result.model_dump(mode="json")
    await db.flush()
    return result


async def cancel_sale(
    db: AsyncSession,
    sale_id: int,
    payload: CancelSaleCreate,
    profile: UserProfile,
    idempotency_key: str,
) -> SaleDetailRead:
    idem = await _idempotency_record(
        db,
        profile,
        idempotency_key,
        request_hash(payload),
        endpoint=f"sales.cancel.{sale_id}",
    )
    if idem.response is not None:
        return SaleDetailRead.model_validate(idem.response)

    sale = await db.scalar(select(Sale).where(Sale.id == sale_id).with_for_update())
    if sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if sale.status is SaleStatus.CANCELADA:
        raise HTTPException(status_code=409, detail="La venta ya esta cancelada")

    payments = list(
        await db.scalars(select(Payment).where(Payment.sale_id == sale.id).order_by(Payment.id))
    )
    cash_payment = next(
        (payment for payment in payments if payment.method is PaymentMethod.EFECTIVO), None
    )
    cash_session: CashSession | None = None
    if cash_payment is not None:
        cash_session = await db.scalar(
            select(CashSession).where(CashSession.id == cash_payment.cash_session_id).with_for_update()
        )
        if cash_session is None or cash_session.status is not CashSessionStatus.ABIERTA:
            raise HTTPException(
                status_code=409,
                detail="La venta en efectivo solo puede cancelarse con la caja abierta",
            )

    items = list(
        await db.scalars(select(SaleItem).where(SaleItem.sale_id == sale.id).order_by(SaleItem.id))
    )
    for item in items:
        balance = await db.scalar(
            select(StockBalance)
            .where(
                StockBalance.branch_id == sale.branch_id,
                StockBalance.variant_id == item.variant_id,
            )
            .with_for_update()
        )
        if balance is None:
            balance = StockBalance(
                branch_id=sale.branch_id,
                variant_id=item.variant_id,
                quantity=0,
            )
            db.add(balance)
        balance.quantity += item.quantity
        db.add(
            StockEntry(
                variant_id=item.variant_id,
                branch_id=sale.branch_id,
                quantity=item.quantity,
                movement_type=StockMovementType.DEVOLUCION,
                reference=f"CANCEL-{sale.folio}",
                note=payload.reason.strip(),
                created_by=profile.id,
            )
        )

    for payment in payments:
        db.add(
            Payment(
                sale_id=sale.id,
                method=payment.method,
                amount=-money(payment.amount),
                cash_session_id=payment.cash_session_id,
            )
        )
        if payment.method is PaymentMethod.EFECTIVO and cash_session is not None:
            db.add(
                CashMovement(
                    cash_session_id=cash_session.id,
                    movement_type=CashMovementType.CANCELACION_VENTA,
                    amount=-money(payment.amount),
                    reference=f"CANCEL-{sale.folio}",
                    created_by=profile.id,
                )
            )

    credit_entries = list(
        await db.scalars(select(CreditEntry).where(CreditEntry.sale_id == sale.id))
    )
    credit_reversal = money(
        sum((entry.quantity for entry in credit_entries if entry.quantity > 0), Decimal(0))
    )
    if credit_reversal:
        current_credit = money(
            await db.scalar(
                select(func.coalesce(func.sum(CreditEntry.quantity), 0)).where(
                    CreditEntry.client_id == sale.client_id
                )
            )
            or 0
        )
        if current_credit < credit_reversal:
            raise HTTPException(
                status_code=409,
                detail="La venta a credito no puede cancelarse mientras tenga abonos aplicados",
            )
    for entry in credit_entries:
        if entry.quantity > 0:
            db.add(
                CreditEntry(
                    client_id=entry.client_id,
                    branch_id=sale.branch_id,
                    quantity=-entry.quantity,
                    movement_type=CreditMovementType.AJUSTE,
                    reference=f"CANCEL-{sale.folio}",
                    note=payload.reason.strip(),
                    sale_id=sale.id,
                    payment_method=PaymentMethod.CREDITO.value,
                    created_by=profile.id,
                )
            )

    sale.status = SaleStatus.CANCELADA
    sale.cancelled_at = datetime.now(UTC)
    sale.cancelled_by = profile.id
    sale.cancellation_reason = payload.reason.strip()
    await db.flush()
    result = await sale_detail(db, sale.id)
    idem.response = result.model_dump(mode="json")
    await db.flush()
    return result


async def sale_detail(db: AsyncSession, sale_id: int) -> SaleDetailRead:
    row = (
        (
            await db.execute(
                select(
                    Sale.id,
                    Sale.folio,
                    Sale.branch_id,
                    Branch.code.label("branch_code"),
                    Sale.client_id,
                    Client.name.label("client_name"),
                    UserProfile.full_name.label("seller_name"),
                    Sale.sale_type,
                    Sale.condition,
                    Sale.status,
                    Sale.payment_method,
                    Sale.subtotal,
                    Sale.discount,
                    Sale.discount_percent,
                    Sale.tax,
                    Sale.total,
                    Sale.discount_approved_by,
                    Sale.cancelled_at,
                    Sale.cancellation_reason,
                    Sale.created_at,
                )
                .join(Branch, Branch.id == Sale.branch_id)
                .outerjoin(Client, Client.id == Sale.client_id)
                .outerjoin(UserProfile, UserProfile.id == Sale.user_id)
                .where(Sale.id == sale_id)
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    items = list(
        await db.scalars(select(SaleItem).where(SaleItem.sale_id == sale_id).order_by(SaleItem.id))
    )
    payments = list(
        await db.scalars(
            select(Payment)
            .where(Payment.sale_id == sale_id)
            .order_by(Payment.created_at, Payment.id)
        )
    )
    return SaleDetailRead(
        **dict(row),
        items=[SaleItemRead.model_validate(item, from_attributes=True) for item in items],
        payments=[
            PaymentRead.model_validate(payment, from_attributes=True) for payment in payments
        ],
    )
