from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query


def pagination_params(
    limit: int = Query(50, ge=1, le=500, description="Máximo de filas por página"),
    offset: int = Query(0, ge=0, description="Filas a saltar"),
) -> tuple[int, int]:
    return limit, offset


PaginationParams = Annotated[tuple[int, int], Depends(pagination_params)]
