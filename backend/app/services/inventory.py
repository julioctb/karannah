from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, tuple_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.catalog import ProductVariant
from app.models.identity import Branch, UserProfile
from app.models.inventory import (
    PhysicalCount,
    PhysicalCountLine,
    PhysicalCountStatus,
    StockBalance,
    StockEntry,
    StockMovementType,
    StockTransfer,
    StockTransferLine,
    StockTransferStatus,
)
from app.models.sales import FolioCounter, IdempotencyRecord
from app.schemas.inventory import (
    PhysicalCountCreate,
    PhysicalCountFinalize,
    PhysicalCountLinesUpdate,
    PhysicalCountRead,
    TransferCreate,
    TransferRead,
    TransferReceive,
    TransferSend,
)


def request_hash(payload: BaseModel) -> str:
    raw = json.dumps(payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


async def idempotency_record(
    db: AsyncSession,
    profile: UserProfile,
    key: str,
    payload_hash: str,
    endpoint: str,
) -> IdempotencyRecord:
    scope = {
        "user_id": profile.id,
        "endpoint": endpoint,
        "key": key,
    }
    if db.get_bind().dialect.name == "postgresql":
        await db.execute(
            pg_insert(IdempotencyRecord)
            .values(id=uuid.uuid4(), request_hash=payload_hash, **scope)
            .on_conflict_do_nothing(index_elements=["user_id", "endpoint", "key"])
        )
    elif await db.scalar(select(IdempotencyRecord).filter_by(**scope)) is None:
        db.add(IdempotencyRecord(request_hash=payload_hash, **scope))
        await db.flush()

    record = await db.scalar(
        select(IdempotencyRecord).filter_by(**scope).with_for_update()
    )
    assert record is not None
    if record.request_hash != payload_hash:
        raise HTTPException(
            status_code=409, detail="Idempotency-Key ya fue usado con otra solicitud"
        )
    return record


async def next_document_folio(
    db: AsyncSession,
    branch: Branch,
    document_type: str,
) -> str:
    year = datetime.now(ZoneInfo(get_settings().business_timezone)).year
    key = {
        "document_type": document_type,
        "branch_id": branch.id,
        "business_year": year,
    }
    if db.get_bind().dialect.name == "postgresql":
        await db.execute(pg_insert(FolioCounter).values(**key).on_conflict_do_nothing())
    elif await db.get(FolioCounter, (document_type, branch.id, year)) is None:
        db.add(FolioCounter(**key))
        await db.flush()
    counter = await db.scalar(select(FolioCounter).filter_by(**key).with_for_update())
    assert counter is not None
    number = counter.next_value
    counter.next_value += 1
    return f"{document_type}-{branch.code}-{year}-{number:06d}"


def stock_balances_lock_statement(keys: list[tuple[uuid.UUID, int]]):
    ordered_keys = sorted(set(keys), key=lambda item: (str(item[0]), item[1]))
    branch_ids = {branch_id for branch_id, _ in ordered_keys}
    if len(branch_ids) == 1:
        branch_id = next(iter(branch_ids))
        return (
            select(StockBalance)
            .where(
                StockBalance.branch_id == branch_id,
                StockBalance.variant_id.in_([variant_id for _, variant_id in ordered_keys]),
            )
            .order_by(StockBalance.variant_id)
            .with_for_update()
        )
    return (
        select(StockBalance)
        .where(tuple_(StockBalance.branch_id, StockBalance.variant_id).in_(ordered_keys))
        .order_by(StockBalance.branch_id, StockBalance.variant_id)
        .with_for_update()
    )


async def ensure_stock_balances(
    db: AsyncSession, keys: list[tuple[uuid.UUID, int]]
) -> None:
    ordered_keys = sorted(set(keys), key=lambda item: (str(item[0]), item[1]))
    if db.get_bind().dialect.name == "postgresql":
        for branch_id, variant_id in ordered_keys:
            await db.execute(
                pg_insert(StockBalance)
                .values(branch_id=branch_id, variant_id=variant_id, quantity=0)
                .on_conflict_do_nothing(index_elements=["branch_id", "variant_id"])
            )
    else:
        existing = {
            (balance.branch_id, balance.variant_id)
            for balance in await db.scalars(stock_balances_lock_statement(ordered_keys))
        }
        for branch_id, variant_id in ordered_keys:
            if (branch_id, variant_id) not in existing:
                db.add(
                    StockBalance(
                        branch_id=branch_id,
                        variant_id=variant_id,
                        quantity=0,
                    )
                )
        await db.flush()


def _transfer_read(transfer: StockTransfer) -> TransferRead:
    return TransferRead(
        id=transfer.id,
        folio=transfer.folio,
        origin_branch_id=transfer.origin_branch_id,
        destination_branch_id=transfer.destination_branch_id,
        status=transfer.status,
        created_by=transfer.created_by,
        sent_by=transfer.sent_by,
        received_by=transfer.received_by,
        created_at=transfer.created_at,
        sent_at=transfer.sent_at,
        received_at=transfer.received_at,
        lines=[
            {
                "id": line.id,
                "variant_id": line.variant_id,
                "shipped_quantity": line.shipped_quantity,
                "received_quantity": line.received_quantity,
                "shortage_quantity": line.shortage_quantity,
            }
            for line in sorted(transfer.lines, key=lambda item: item.variant_id)
        ],
    )


async def _load_transfer(
    db: AsyncSession,
    transfer_id: uuid.UUID,
    visible_branch_ids: list[uuid.UUID],
    *,
    for_update: bool = False,
) -> StockTransfer:
    statement = (
        select(StockTransfer)
        .options(selectinload(StockTransfer.lines))
        .where(
            StockTransfer.id == transfer_id,
            StockTransfer.origin_branch_id.in_(visible_branch_ids),
            StockTransfer.destination_branch_id.in_(visible_branch_ids),
        )
    )
    if for_update:
        statement = statement.with_for_update()
    transfer = await db.scalar(statement)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transferencia no encontrada")
    return transfer


async def create_transfer(
    db: AsyncSession,
    payload: TransferCreate,
    profile: UserProfile,
    origin_branch: Branch,
) -> TransferRead:
    if payload.origin_branch_id == payload.destination_branch_id:
        raise HTTPException(status_code=409, detail="Las sucursales deben ser distintas")
    variant_ids = [line.variant_id for line in payload.lines]
    if len(variant_ids) != len(set(variant_ids)):
        raise HTTPException(status_code=409, detail="La transferencia repite variantes")
    active_variant_ids = set(
        await db.scalars(
            select(ProductVariant.id).where(
                ProductVariant.id.in_(variant_ids), ProductVariant.active.is_(True)
            )
        )
    )
    if active_variant_ids != set(variant_ids):
        raise HTTPException(status_code=404, detail="Variante activa no encontrada")

    transfer = StockTransfer(
        folio=await next_document_folio(db, origin_branch, "TR"),
        origin_branch_id=payload.origin_branch_id,
        destination_branch_id=payload.destination_branch_id,
        created_by=profile.id,
        lines=[
            StockTransferLine(
                variant_id=line.variant_id,
                shipped_quantity=line.shipped_quantity,
            )
            for line in payload.lines
        ],
    )
    db.add(transfer)
    await db.flush()
    return _transfer_read(transfer)


async def list_transfers(
    db: AsyncSession, visible_branch_ids: list[uuid.UUID], limit: int, offset: int
) -> list[TransferRead]:
    if not visible_branch_ids:
        return []
    transfers = list(
        await db.scalars(
            select(StockTransfer)
            .options(selectinload(StockTransfer.lines))
            .where(
                StockTransfer.origin_branch_id.in_(visible_branch_ids),
                StockTransfer.destination_branch_id.in_(visible_branch_ids),
            )
            .order_by(StockTransfer.created_at.desc(), StockTransfer.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return [_transfer_read(transfer) for transfer in transfers]


async def transfer_detail(
    db: AsyncSession, transfer_id: uuid.UUID, visible_branch_ids: list[uuid.UUID]
) -> TransferRead:
    return _transfer_read(await _load_transfer(db, transfer_id, visible_branch_ids))


async def send_transfer(
    db: AsyncSession,
    transfer_id: uuid.UUID,
    payload: TransferSend,
    profile: UserProfile,
    visible_branch_ids: list[uuid.UUID],
    idempotency_key: str,
) -> TransferRead:
    transfer = await _load_transfer(db, transfer_id, visible_branch_ids, for_update=True)
    idem = await idempotency_record(
        db,
        profile,
        idempotency_key,
        request_hash(payload),
        f"inventory.transfers.{transfer_id}.send",
    )
    if idem.response is not None:
        return TransferRead.model_validate(idem.response)

    if transfer.status is not StockTransferStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Solo se puede enviar una transferencia draft")
    keys = [(transfer.origin_branch_id, line.variant_id) for line in transfer.lines]
    balances = {
        (balance.branch_id, balance.variant_id): balance
        for balance in await db.scalars(stock_balances_lock_statement(keys))
    }
    for line in transfer.lines:
        balance = balances.get((transfer.origin_branch_id, line.variant_id))
        if balance is None or balance.quantity < line.shipped_quantity:
            raise HTTPException(status_code=409, detail="Stock insuficiente para la transferencia")
    note = payload.note.strip() if payload.note else None
    for line in transfer.lines:
        balance = balances[(transfer.origin_branch_id, line.variant_id)]
        balance.quantity -= line.shipped_quantity
        db.add(
            StockEntry(
                variant_id=line.variant_id,
                branch_id=transfer.origin_branch_id,
                quantity=-line.shipped_quantity,
                movement_type=StockMovementType.TRANSFERENCIA_SALIDA,
                reference=transfer.folio,
                note=note,
                created_by=profile.id,
            )
        )
    transfer.status = StockTransferStatus.SENT
    transfer.sent_by = profile.id
    transfer.sent_at = datetime.now(UTC)
    await db.flush()
    result = _transfer_read(transfer)
    idem.response = result.model_dump(mode="json")
    await db.flush()
    return result


async def receive_transfer(
    db: AsyncSession,
    transfer_id: uuid.UUID,
    payload: TransferReceive,
    profile: UserProfile,
    visible_branch_ids: list[uuid.UUID],
    idempotency_key: str,
) -> TransferRead:
    transfer = await _load_transfer(db, transfer_id, visible_branch_ids, for_update=True)
    idem = await idempotency_record(
        db,
        profile,
        idempotency_key,
        request_hash(payload),
        f"inventory.transfers.{transfer_id}.receive",
    )
    if idem.response is not None:
        return TransferRead.model_validate(idem.response)

    if transfer.status is not StockTransferStatus.SENT:
        raise HTTPException(status_code=409, detail="Solo se puede recibir una transferencia sent")
    received_by_variant = {line.variant_id: line.received_quantity for line in payload.lines}
    if len(received_by_variant) != len(payload.lines) or set(received_by_variant) != {
        line.variant_id for line in transfer.lines
    }:
        raise HTTPException(status_code=409, detail="Las lineas recibidas no coinciden")
    for line in transfer.lines:
        if received_by_variant[line.variant_id] > line.shipped_quantity:
            raise HTTPException(status_code=409, detail="La recepcion supera la cantidad enviada")

    positive_keys = [
        (transfer.destination_branch_id, line.variant_id)
        for line in transfer.lines
        if received_by_variant[line.variant_id] > 0
    ]
    if positive_keys:
        await ensure_stock_balances(db, positive_keys)
        balances = {
            (balance.branch_id, balance.variant_id): balance
            for balance in await db.scalars(stock_balances_lock_statement(positive_keys))
        }
    else:
        balances = {}
    for line in transfer.lines:
        received = received_by_variant[line.variant_id]
        line.received_quantity = received
        line.shortage_quantity = line.shipped_quantity - received
        if received > 0:
            balances[(transfer.destination_branch_id, line.variant_id)].quantity += received
            db.add(
                StockEntry(
                    variant_id=line.variant_id,
                    branch_id=transfer.destination_branch_id,
                    quantity=received,
                    movement_type=StockMovementType.TRANSFERENCIA_ENTRADA,
                    reference=transfer.folio,
                    created_by=profile.id,
                )
            )
    transfer.status = StockTransferStatus.RECEIVED
    transfer.received_by = profile.id
    transfer.received_at = datetime.now(UTC)
    await db.flush()
    result = _transfer_read(transfer)
    idem.response = result.model_dump(mode="json")
    await db.flush()
    return result


def _physical_count_read(count: PhysicalCount) -> PhysicalCountRead:
    return PhysicalCountRead(
        id=count.id,
        folio=count.folio,
        branch_id=count.branch_id,
        status=count.status,
        created_by=count.created_by,
        finalized_by=count.finalized_by,
        created_at=count.created_at,
        finalized_at=count.finalized_at,
        lines=[
            {
                "id": line.id,
                "variant_id": line.variant_id,
                "snapshot_quantity": line.snapshot_quantity,
                "observed_quantity": line.observed_quantity,
            }
            for line in sorted(count.lines, key=lambda item: item.variant_id)
        ],
    )


async def _load_physical_count(
    db: AsyncSession,
    count_id: uuid.UUID,
    visible_branch_ids: list[uuid.UUID],
    *,
    for_update: bool = False,
) -> PhysicalCount:
    statement = (
        select(PhysicalCount)
        .options(selectinload(PhysicalCount.lines))
        .where(
            PhysicalCount.id == count_id,
            PhysicalCount.branch_id.in_(visible_branch_ids),
        )
    )
    if for_update:
        statement = statement.with_for_update()
    count = await db.scalar(statement)
    if count is None:
        raise HTTPException(status_code=404, detail="Conteo fisico no encontrado")
    return count


async def create_physical_count(
    db: AsyncSession,
    payload: PhysicalCountCreate,
    profile: UserProfile,
    branch: Branch,
    idempotency_key: str,
) -> PhysicalCountRead:
    idem = await idempotency_record(
        db,
        profile,
        idempotency_key,
        request_hash(payload),
        "inventory.physical-counts.create",
    )
    if idem.response is not None:
        return PhysicalCountRead.model_validate(idem.response)

    snapshot_rows = (
        await db.execute(
            select(StockBalance.variant_id, StockBalance.quantity)
            .join(ProductVariant, ProductVariant.id == StockBalance.variant_id)
            .where(
                StockBalance.branch_id == payload.branch_id,
                ProductVariant.active.is_(True),
            )
            .order_by(StockBalance.variant_id)
        )
    ).all()
    count = PhysicalCount(
        folio=await next_document_folio(db, branch, "CF"),
        branch_id=payload.branch_id,
        created_by=profile.id,
        lines=[
            PhysicalCountLine(variant_id=variant_id, snapshot_quantity=quantity)
            for variant_id, quantity in snapshot_rows
        ],
    )
    db.add(count)
    await db.flush()
    result = _physical_count_read(count)
    idem.response = result.model_dump(mode="json")
    await db.flush()
    return result


async def list_physical_counts(
    db: AsyncSession, visible_branch_ids: list[uuid.UUID], limit: int, offset: int
) -> list[PhysicalCountRead]:
    if not visible_branch_ids:
        return []
    counts = list(
        await db.scalars(
            select(PhysicalCount)
            .options(selectinload(PhysicalCount.lines))
            .where(PhysicalCount.branch_id.in_(visible_branch_ids))
            .order_by(PhysicalCount.created_at.desc(), PhysicalCount.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return [_physical_count_read(count) for count in counts]


async def physical_count_detail(
    db: AsyncSession, count_id: uuid.UUID, visible_branch_ids: list[uuid.UUID]
) -> PhysicalCountRead:
    return _physical_count_read(
        await _load_physical_count(db, count_id, visible_branch_ids)
    )


async def update_physical_count_lines(
    db: AsyncSession,
    count_id: uuid.UUID,
    payload: PhysicalCountLinesUpdate,
    visible_branch_ids: list[uuid.UUID],
) -> PhysicalCountRead:
    count = await _load_physical_count(db, count_id, visible_branch_ids, for_update=True)
    if count.status is not PhysicalCountStatus.OPEN:
        raise HTTPException(status_code=409, detail="Solo se puede editar un conteo open")
    observed_by_variant = {
        line.variant_id: line.observed_quantity for line in payload.lines
    }
    if len(observed_by_variant) != len(payload.lines):
        raise HTTPException(status_code=409, detail="Las observaciones repiten variantes")
    lines_by_variant = {line.variant_id: line for line in count.lines}
    if not set(observed_by_variant).issubset(lines_by_variant):
        raise HTTPException(status_code=409, detail="La variante no pertenece al conteo")
    for variant_id, observed_quantity in observed_by_variant.items():
        lines_by_variant[variant_id].observed_quantity = observed_quantity
    await db.flush()
    return _physical_count_read(count)


async def finalize_physical_count(
    db: AsyncSession,
    count_id: uuid.UUID,
    payload: PhysicalCountFinalize,
    profile: UserProfile,
    visible_branch_ids: list[uuid.UUID],
    idempotency_key: str,
) -> PhysicalCountRead:
    count = await _load_physical_count(db, count_id, visible_branch_ids, for_update=True)
    idem = await idempotency_record(
        db,
        profile,
        idempotency_key,
        request_hash(payload),
        f"inventory.physical-counts.{count_id}.finalize",
    )
    if idem.response is not None:
        return PhysicalCountRead.model_validate(idem.response)
    if count.status is not PhysicalCountStatus.OPEN:
        raise HTTPException(status_code=409, detail="El conteo ya fue finalizado")
    if any(line.observed_quantity is None for line in count.lines):
        raise HTTPException(status_code=409, detail="Todas las lineas requieren observacion")

    keys = [(count.branch_id, line.variant_id) for line in count.lines]
    balances = {
        (balance.branch_id, balance.variant_id): balance
        for balance in await db.scalars(stock_balances_lock_statement(keys))
    }
    if len(balances) != len(keys):
        raise HTTPException(status_code=409, detail="El inventario del conteo ya no existe")
    differences = {
        line.variant_id: line.observed_quantity
        - balances[(count.branch_id, line.variant_id)].quantity
        for line in count.lines
    }
    if any(
        balances[(count.branch_id, line.variant_id)].quantity
        + differences[line.variant_id]
        < 0
        for line in count.lines
    ):
        raise HTTPException(
            status_code=409, detail="El conteo produciria inventario negativo"
        )

    note = payload.note.strip() if payload.note else None
    for line in count.lines:
        difference = differences[line.variant_id]
        if difference == 0:
            continue
        balances[(count.branch_id, line.variant_id)].quantity += difference
        db.add(
            StockEntry(
                variant_id=line.variant_id,
                branch_id=count.branch_id,
                quantity=difference,
                movement_type=StockMovementType.CONTEO,
                reference=count.folio,
                note=note,
                created_by=profile.id,
            )
        )
    count.status = PhysicalCountStatus.FINALIZED
    count.finalized_by = profile.id
    count.finalized_at = datetime.now(UTC)
    await db.flush()
    result = _physical_count_read(count)
    idem.response = result.model_dump(mode="json")
    await db.flush()
    return result
