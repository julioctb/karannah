from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clients import Client
from app.models.identity import Branch, UserProfile
from app.models.repairs import Repair, RepairStatus, RepairStatusHistory
from app.models.sales import Payment, Sale, SaleStatus
from app.schemas.repairs import (
    RepairCharge,
    RepairCreate,
    RepairRead,
    RepairTransition,
    RepairUpdate,
)
from app.services.inventory import idempotency_record, next_document_folio, request_hash
from app.services.pos import create_repair_sale, money

_CREATE_ENDPOINT = "POST /repairs"


async def _registered_client_name(db: AsyncSession, client_id: int) -> str:
    client = await db.scalar(
        select(Client).where(Client.id == client_id, Client.active.is_(True))
    )
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client.name


async def repair_read(db: AsyncSession, repair: Repair) -> RepairRead:
    values = RepairRead.model_validate(repair).model_dump()
    price = money(repair.price or 0)
    paid_amount = money(0)
    active_sale = False
    if repair.sale_id is not None:
        sale = await db.get(Sale, repair.sale_id)
        if sale is not None:
            paid_amount = money(
                await db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0)).where(
                        Payment.sale_id == sale.id
                    )
                )
                or 0
            )
            active_sale = sale.status is SaleStatus.CONFIRMADA
            price = money(sale.total)
    balance = money(max(price - paid_amount, Decimal(0)))
    values.update(
        paid_amount=paid_amount,
        balance=balance,
        paid_enough=active_sale and balance == 0,
    )
    return RepairRead.model_validate(values)


async def repair_reads(db: AsyncSession, repairs: list[Repair]) -> list[RepairRead]:
    return [await repair_read(db, repair) for repair in repairs]


async def create_repair(
    db: AsyncSession,
    payload: RepairCreate,
    profile: UserProfile,
    branch: Branch,
    idempotency_key: str,
) -> RepairRead:
    idem = await idempotency_record(
        db,
        profile,
        idempotency_key,
        request_hash(payload),
        _CREATE_ENDPOINT,
    )
    if idem.response is not None:
        return RepairRead.model_validate(idem.response)

    client_name = payload.client_name
    if payload.client_id is not None:
        client_name = await _registered_client_name(db, payload.client_id)
    assert client_name is not None

    repair = Repair(
        folio=await next_document_folio(db, branch, "RP"),
        branch_id=branch.id,
        client_id=payload.client_id,
        client_name=client_name,
        product_description=payload.product_description,
        service=payload.service,
        status=RepairStatus.RECEIVED,
        price=payload.price,
        received_at=payload.received_at,
        expected_at=payload.expected_at,
        notes=payload.notes or None,
    )
    db.add(repair)
    await db.flush()
    db.add(
        RepairStatusHistory(
            repair_id=repair.id,
            from_status=None,
            to_status=RepairStatus.RECEIVED,
            actor_id=profile.id,
        )
    )
    result = await repair_read(db, repair)
    idem.response = result.model_dump(mode="json")
    return result


async def update_repair(
    db: AsyncSession,
    repair_id: int,
    payload: RepairUpdate,
    visible_branch_ids: list[uuid.UUID],
) -> RepairRead:
    repair = await db.scalar(
        select(Repair)
        .where(
            Repair.id == repair_id,
            Repair.branch_id.in_(visible_branch_ids),
        )
        .with_for_update()
    )
    if repair is None:
        raise HTTPException(status_code=404, detail="Reparacion no encontrada")
    if repair.delivered_at is not None:
        raise HTTPException(status_code=409, detail="La reparacion ya fue entregada")
    if repair.blocked_for_review:
        raise HTTPException(status_code=409, detail="La reparacion requiere revision")

    changes: dict[str, Any] = payload.model_dump(exclude_unset=True)
    if repair.sale_id is not None and "price" in changes:
        raise HTTPException(
            status_code=409, detail="El precio no puede cambiar despues del cobro"
        )
    customer_fields = {"client_id", "client_name", "confirm_free_text_client"}
    if customer_fields & changes.keys():
        client_id = changes.get("client_id", repair.client_id)
        if client_id is not None:
            if "client_name" in changes and "client_id" not in changes:
                raise HTTPException(
                    status_code=422,
                    detail="El nombre de un cliente registrado no es editable aqui",
                )
            repair.client_id = client_id
            repair.client_name = await _registered_client_name(db, client_id)
        else:
            raw_client_name = changes.get("client_name", repair.client_name)
            client_name = (
                raw_client_name.strip() if isinstance(raw_client_name, str) else ""
            )
            if not client_name or not payload.confirm_free_text_client:
                raise HTTPException(
                    status_code=422,
                    detail="Cliente libre requiere nombre y confirmacion explicita",
                )
            repair.client_id = None
            repair.client_name = client_name

    received_at = changes.get("received_at", repair.received_at)
    expected_at = changes.get("expected_at", repair.expected_at)
    if received_at is None:
        raise HTTPException(status_code=422, detail="received_at es obligatorio")
    if expected_at is not None and expected_at < received_at:
        raise HTTPException(
            status_code=422, detail="expected_at no puede ser anterior a received_at"
        )

    for field in (
        "product_description",
        "service",
        "price",
        "received_at",
        "expected_at",
        "notes",
    ):
        if field in changes:
            value = changes[field]
            if field in {"product_description", "service"} and value is None:
                raise HTTPException(status_code=422, detail=f"{field} es obligatorio")
            if field == "notes":
                value = value or None
            setattr(repair, field, value)

    await db.flush()
    return await repair_read(db, repair)


async def charge_repair(
    db: AsyncSession,
    repair_id: int,
    payload: RepairCharge,
    profile: UserProfile,
    visible_branch_ids: list[uuid.UUID],
    idempotency_key: str,
) -> RepairRead:
    idem = await idempotency_record(
        db,
        profile,
        idempotency_key,
        request_hash(payload),
        f"POST /repairs/{repair_id}/charge",
    )
    if idem.response is not None:
        return RepairRead.model_validate(idem.response)

    repair = await db.scalar(
        select(Repair)
        .where(
            Repair.id == repair_id,
            Repair.branch_id.in_(visible_branch_ids),
        )
        .with_for_update()
    )
    if repair is None:
        raise HTTPException(status_code=404, detail="Reparacion no encontrada")
    if repair.delivered_at is not None:
        raise HTTPException(status_code=409, detail="La reparacion ya fue entregada")
    if repair.blocked_for_review:
        raise HTTPException(status_code=409, detail="La reparacion requiere revision")
    if repair.sale_id is not None:
        raise HTTPException(status_code=409, detail="La reparacion ya tiene una venta")
    if repair.branch_id is None:
        raise HTTPException(
            status_code=409, detail="La reparacion heredada no tiene sucursal"
        )
    branch = await db.get(Branch, repair.branch_id)
    assert branch is not None

    sale = await create_repair_sale(db, repair, payload, profile, branch)
    repair.sale_id = sale.id
    await db.flush()
    result = await repair_read(db, repair)
    idem.response = result.model_dump(mode="json")
    await db.flush()
    return result


async def transition_repair(
    db: AsyncSession,
    repair_id: int,
    payload: RepairTransition,
    profile: UserProfile,
    visible_branch_ids: list[uuid.UUID],
) -> RepairRead:
    repair = await db.scalar(
        select(Repair)
        .where(
            Repair.id == repair_id,
            Repair.branch_id.in_(visible_branch_ids),
        )
        .with_for_update()
    )
    if repair is None:
        raise HTTPException(status_code=404, detail="Reparacion no encontrada")
    if repair.delivered_at is not None:
        raise HTTPException(status_code=409, detail="La reparacion ya fue entregada")
    if repair.blocked_for_review:
        raise HTTPException(status_code=409, detail="La reparacion requiere revision")

    from_status = repair.status
    to_status = payload.to_status
    if from_status == to_status:
        raise HTTPException(status_code=409, detail="La reparacion ya tiene ese estado")

    allowed_transitions = {
        RepairStatus.RECEIVED: {RepairStatus.IN_WORKSHOP},
        RepairStatus.IN_WORKSHOP: {RepairStatus.READY},
        RepairStatus.READY: {RepairStatus.IN_WORKSHOP},
    }
    if to_status not in allowed_transitions[from_status]:
        raise HTTPException(status_code=409, detail="Transicion de estado no permitida")
    if (
        from_status == RepairStatus.READY
        and to_status == RepairStatus.IN_WORKSHOP
        and payload.note is None
    ):
        raise HTTPException(
            status_code=422,
            detail="La reapertura de una reparacion lista requiere una razon",
        )

    repair.status = to_status
    if to_status == RepairStatus.READY and repair.completed_at is None:
        repair.completed_at = datetime.now(UTC).date()
    db.add(
        RepairStatusHistory(
            repair_id=repair.id,
            from_status=from_status,
            to_status=to_status,
            actor_id=profile.id,
            note=payload.note,
        )
    )
    await db.flush()
    return await repair_read(db, repair)
