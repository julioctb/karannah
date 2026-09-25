from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Category, Material, SkuCounter


async def allocate_skus(
    db: AsyncSession,
    category: Category,
    material: Material | None,
    count: int,
) -> list[str]:
    """Reserva una secuencia por categoria dentro de la transaccion actual."""
    counter = (
        await db.execute(
            select(SkuCounter).where(SkuCounter.category_id == category.id).with_for_update()
        )
    ).scalar_one_or_none()
    if counter is None:
        counter = SkuCounter(category_id=category.id, next_value=1)
        db.add(counter)
        await db.flush()

    start = counter.next_value
    counter.next_value += count
    prefix = category.code.upper()
    if category.requires_material and material is not None:
        prefix = f"{prefix}-{material.code.upper()}"
    return [f"{prefix}-{value:04d}" for value in range(start, start + count)]
