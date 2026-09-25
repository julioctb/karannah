from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ensure_role, get_current_profile, require_visible_branch
from app.api.pagination import PaginationParams
from app.core.db import get_db
from app.models.cash import CashMovement, CashMovementType
from app.models.clients import Client, ClientType, CreditEntry, CreditMovementType
from app.models.identity import Branch, Role, UserProfile
from app.models.sales import PaymentMethod
from app.schemas.clients import (
    ClientCommercialUpdate,
    ClientCreate,
    ClientRead,
    ClientUpdate,
    CreditLedgerRead,
    CreditPaymentCreate,
    CreditPaymentRead,
)
from app.services.pos import _idempotency_record, lock_open_cash_session, money, request_hash

router = APIRouter(prefix="/clients", tags=["clients"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


def _client_statement():  # type: ignore[no-untyped-def]
    balance = (
        select(
            CreditEntry.client_id.label("client_id"),
            func.coalesce(func.sum(CreditEntry.quantity), 0).label("credit_balance"),
        )
        .group_by(CreditEntry.client_id)
        .subquery()
    )
    return (
        select(
            Client.id,
            Client.name,
            Client.type,
            Client.phone,
            Client.email,
            Client.credit_limit,
            Client.notes,
            Client.active,
            Client.created_at,
            func.coalesce(balance.c.credit_balance, 0).label("credit_balance"),
        )
        .outerjoin(balance, balance.c.client_id == Client.id)
        .order_by(Client.name)
    )


async def _read_client(db: AsyncSession, client_id: int) -> ClientRead:
    row = (
        (await db.execute(_client_statement().where(Client.id == client_id)))
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return ClientRead.model_validate(dict(row))


@router.get("", response_model=list[ClientRead])
async def list_clients(
    db: Db,
    _profile: Profile,
    page: PaginationParams,
    search: Annotated[str | None, Query(max_length=120)] = None,
    type: Annotated[ClientType | None, Query()] = None,
) -> list[ClientRead]:
    limit, offset = page
    stmt = _client_statement()
    if search:
        like = f"%{search}%"
        stmt = stmt.where(Client.name.ilike(like) | Client.phone.ilike(like))
    if type is not None:
        stmt = stmt.where(Client.type == type)
    rows = (await db.execute(stmt.limit(limit).offset(offset))).mappings().all()
    return [ClientRead.model_validate(dict(row)) for row in rows]


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(client_id: int, db: Db, _profile: Profile) -> ClientRead:
    return await _read_client(db, client_id)


@router.get("/{client_id}/credit-ledger", response_model=list[CreditLedgerRead])
async def list_credit_ledger(
    client_id: int, db: Db, _profile: Profile, page: PaginationParams
) -> list[CreditLedgerRead]:
    if await db.get(Client, client_id) is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    limit, offset = page
    rows = (
        await db.execute(
            select(
                CreditEntry.id,
                CreditEntry.client_id,
                CreditEntry.branch_id,
                Branch.code.label("branch_code"),
                CreditEntry.quantity,
                CreditEntry.movement_type,
                CreditEntry.reference,
                CreditEntry.note,
                CreditEntry.sale_id,
                CreditEntry.payment_method,
                CreditEntry.cash_session_id,
                CreditEntry.created_by,
                CreditEntry.created_at,
            )
            .outerjoin(Branch, Branch.id == CreditEntry.branch_id)
            .where(CreditEntry.client_id == client_id)
            .order_by(CreditEntry.created_at.desc(), CreditEntry.id.desc())
            .limit(limit)
            .offset(offset)
        )
    ).mappings()
    return [CreditLedgerRead.model_validate(dict(row)) for row in rows]


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate, db: Db, _profile: Profile) -> ClientRead:
    row = Client(
        name=payload.name.strip(),
        type=ClientType.MENUDEO,
        phone=payload.phone.strip() if payload.phone else None,
        email=payload.email.strip().lower() if payload.email else None,
        credit_limit=None,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return await _read_client(db, row.id)


@router.post(
    "/{client_id}/credit-payments",
    response_model=CreditPaymentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_credit_payment(
    client_id: int,
    payload: CreditPaymentCreate,
    db: Db,
    profile: Profile,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=120)],
) -> CreditPaymentRead:
    key = idempotency_key.strip()
    if not key:
        raise HTTPException(status_code=422, detail="Idempotency-Key no puede estar vacio")
    idem = await _idempotency_record(
        db,
        profile,
        key,
        request_hash(payload),
        endpoint=f"clients.credit-payment.{client_id}",
    )
    if idem.response is not None:
        return CreditPaymentRead.model_validate(idem.response)

    await require_visible_branch(db, profile, payload.branch_id)
    cash_session = None
    if payload.method is PaymentMethod.EFECTIVO:
        assert payload.cash_session_id is not None
        cash_session = await lock_open_cash_session(db, payload.cash_session_id, payload.branch_id)
    client = await db.scalar(select(Client).where(Client.id == client_id).with_for_update())
    if client is None or not client.active:
        raise HTTPException(status_code=404, detail="Cliente activo no encontrado")
    balance = money(
        await db.scalar(
            select(func.coalesce(func.sum(CreditEntry.quantity), 0)).where(
                CreditEntry.client_id == client_id
            )
        )
        or 0
    )
    amount = money(payload.amount)
    if balance <= 0 or amount > balance:
        raise HTTPException(status_code=409, detail="El abono excede el saldo del cliente")
    entry = CreditEntry(
        client_id=client_id,
        branch_id=payload.branch_id,
        quantity=-amount,
        movement_type=CreditMovementType.ABONO,
        payment_method=payload.method.value,
        cash_session_id=cash_session.id if cash_session else None,
        created_by=profile.id,
    )
    db.add(entry)
    await db.flush()
    entry.reference = f"ABONO-{entry.id}"
    if cash_session is not None:
        db.add(
            CashMovement(
                cash_session_id=cash_session.id,
                movement_type=CashMovementType.ABONO_CREDITO,
                amount=amount,
                reference=entry.reference,
                created_by=profile.id,
            )
        )
    await db.flush()
    await db.refresh(entry)
    result = CreditPaymentRead(
        id=entry.id,
        client_id=client_id,
        amount=amount,
        method=payload.method,
        cash_session_id=entry.cash_session_id,
        resulting_balance=money(balance - amount),
        created_at=entry.created_at,
    )
    idem.response = result.model_dump(mode="json")
    await db.commit()
    return result


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: int, payload: ClientUpdate, db: Db, _profile: Profile
) -> ClientRead:
    row = await db.get(Client, client_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if isinstance(value, str):
            value = value.strip().lower() if field == "email" else value.strip()
        setattr(row, field, value or None)
    if not row.name:
        raise HTTPException(status_code=422, detail="El nombre es obligatorio")
    await db.commit()
    return await _read_client(db, row.id)


@router.patch("/{client_id}/commercial-profile", response_model=ClientRead)
async def update_commercial_profile(
    client_id: int, payload: ClientCommercialUpdate, db: Db, profile: Profile
) -> ClientRead:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Client, client_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    row.type = payload.type
    row.credit_limit = payload.credit_limit if payload.type is ClientType.MAYOREO else None
    await db.commit()
    return await _read_client(db, row.id)
