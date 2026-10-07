from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    auth as auth_routes,
)
from app.api.v1 import (
    cash,
    catalog,
    clients,
    inventory,
    promotions,
    repairs,
    reports,
    sales,
    settings,
)
from app.api.v1 import (
    me as me_routes,
)

api_router = APIRouter()
api_router.include_router(auth_routes.router)
api_router.include_router(me_routes.router)
api_router.include_router(catalog.router)
api_router.include_router(cash.router)
api_router.include_router(inventory.router)
api_router.include_router(clients.router)
api_router.include_router(promotions.router)
api_router.include_router(sales.router)
api_router.include_router(repairs.router)
api_router.include_router(reports.router)
api_router.include_router(settings.router)
