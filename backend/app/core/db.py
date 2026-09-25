from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Engine async de SQLAlchemy (lazy, bajo demanda).

    Nota: `DATABASE_URL` debe usar el driver `postgresql+asyncpg://`.
    Se construye perezosamente para que la app pueda importarse sin DB
    (tests unitarios / smoke de /health).
    """
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL no está configurado: no se puede abrir conexión a Postgres."
            )
        _engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _session_factory is not None
    return _session_factory


async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependencia de FastAPI: una sesión por request, rollback en error."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Cierra el pool de conexiones (llamado en el shutdown de la app)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
