from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.db import dispose_engine
from app.services.product_images import build_product_image_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_runtime()
    yield
    await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.state.product_image_service = build_product_image_service(settings)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
app.mount(
    settings.product_media_url,
    StaticFiles(directory=settings.product_media_root),
    name="product-media",
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
