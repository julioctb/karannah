from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    ensure_role,
    get_current_profile,
    require_visible_branch,
    visible_branch_ids,
)
from app.core.config import get_settings
from app.core.db import get_db
from app.models.cash import CashSession, CashSessionStatus, Terminal
from app.models.identity import Branch, Role, UserProfile
from app.schemas.cash import CashSessionClose, CashSessionOpen, CashSessionRead, TerminalRead
from app.services.pos import expected_cash, money

router = APIRouter(prefix="/cash", tags=["cash"])

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]


async def _session_read(db: AsyncSession, row: CashSession) -> CashSessionRead:
    current_expected = row.expected_cash
    if current_expected is None:
        current_expected = await expected_cash(db, row)
    return CashSessionRead(
        id=row.id,
        terminal_id=row.terminal_id,
        branch_id=row.branch_id,
        opening_amount=row.opening_amount,
        expected_cash=current_expected,
        counted_cash=row.counted_cash,
        variance=row.variance,
        opened_by=row.opened_by,
        closed_by=row.closed_by,
        status=row.status,
        business_date=row.business_date,
        opened_at=row.opened_at,
        closed_at=row.closed_at,
    )


@router.get("/terminals", response_model=list[TerminalRead])
async def list_terminals(db: Db, profile: Profile) -> list[TerminalRead]:
    branch_ids = await visible_branch_ids(db, profile)
    if not branch_ids:
        return []
    rows = (
        await db.execute(
            select(
                Terminal.id,
                Terminal.branch_id,
                Branch.code.label("branch_code"),
                Terminal.code,
                Terminal.name,
                Terminal.active,
            )
            .join(Branch, Branch.id == Terminal.branch_id)
            .where(Terminal.branch_id.in_(branch_ids), Terminal.active.is_(True))
            .order_by(Branch.code, Terminal.code)
        )
    ).mappings()
    return [TerminalRead.model_validate(dict(row)) for row in rows]


@router.get("/sessions/current", response_model=CashSessionRead | None)
async def current_session(
    db: Db,
    profile: Profile,
    terminal_id: Annotated[uuid.UUID, Query()],
) -> CashSessionRead | None:
    terminal = await db.get(Terminal, terminal_id)
    if terminal is None or not terminal.active:
        raise HTTPException(status_code=404, detail="Terminal no encontrada")
    await require_visible_branch(db, profile, terminal.branch_id)
    row = await db.scalar(
        select(CashSession).where(
            CashSession.terminal_id == terminal_id,
            CashSession.status == CashSessionStatus.ABIERTA,
        )
    )
    return await _session_read(db, row) if row else None


@router.post("/sessions/open", response_model=CashSessionRead, status_code=status.HTTP_201_CREATED)
async def open_session(payload: CashSessionOpen, db: Db, profile: Profile) -> CashSessionRead:
    ensure_role(profile, Role.VENDEDOR, Role.ENCARGADO, Role.ADMIN)
    terminal = await db.scalar(
        select(Terminal).where(Terminal.id == payload.terminal_id).with_for_update()
    )
    if terminal is None or not terminal.active:
        raise HTTPException(status_code=404, detail="Terminal no encontrada")
    await require_visible_branch(db, profile, terminal.branch_id)
    existing = await db.scalar(
        select(CashSession.id).where(
            CashSession.terminal_id == terminal.id,
            CashSession.status == CashSessionStatus.ABIERTA,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="La terminal ya tiene una sesion abierta")
    row = CashSession(
        terminal_id=terminal.id,
        branch_id=terminal.branch_id,
        opening_amount=money(payload.opening_amount),
        opened_by=profile.id,
        status=CashSessionStatus.ABIERTA,
        business_date=datetime.now(ZoneInfo(get_settings().business_timezone)).date(),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return await _session_read(db, row)


@router.post("/sessions/{session_id}/close", response_model=CashSessionRead)
async def close_session(
    session_id: uuid.UUID, payload: CashSessionClose, db: Db, profile: Profile
) -> CashSessionRead:
    ensure_role(profile, Role.ENCARGADO, Role.ADMIN)
    row = await db.scalar(select(CashSession).where(CashSession.id == session_id).with_for_update())
    if row is None:
        raise HTTPException(status_code=404, detail="Sesion de caja no encontrada")
    await require_visible_branch(db, profile, row.branch_id)
    if row.status is not CashSessionStatus.ABIERTA:
        raise HTTPException(status_code=409, detail="La sesion de caja ya esta cerrada")
    expected = await expected_cash(db, row)
    counted = money(payload.counted_cash)
    row.expected_cash = expected
    row.counted_cash = counted
    row.variance = money(counted - expected)
    row.closed_by = profile.id
    row.closed_at = datetime.now(UTC)
    row.status = CashSessionStatus.CERRADA
    await db.commit()
    await db.refresh(row)
    return await _session_read(db, row)
