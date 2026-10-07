from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clients import Client
from app.models.identity import Branch, UserProfile
from app.models.repairs import Repair, RepairStatus, RepairStatusHistory
from app.schemas.repairs import RepairCreate, RepairRead, RepairUpdate
from app.services.inventory import idempotency_record, next_document_folio, request_hash

_CREATE_ENDPOINT = "POST /repairs"


async def _registered_client_name(db: AsyncSession, client_id: int) -> str:
    client = await db.scalar(
        select(Client).where(Client.id == client_id, Client.active.is_(True))
    )
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client.name


def _repair_read(repair: Repair) -> RepairRead:
    return RepairRead.model_validate(repair)


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
    result = _repair_read(repair)
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
    return _repair_read(repair)
