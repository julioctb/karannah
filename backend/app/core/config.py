from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API cargada desde variables de entorno / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Joyería API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"

    # CORS: lista separada por comas de orígenes permitidos.
    cors_origins: str = "http://localhost:5173"

    # PostgreSQL local durante el desarrollo; Supabase queda para la Fase 9.
    database_url: str = ""

    # Proveedor de auth: "supabase" (JWKS RS256/ES256) o "local" (JWT HMAC, solo dev).
    auth_provider: str = "supabase"
    local_jwt_secret: str = "dev-insecure-local-jwt-secret"
    local_jwt_expire_minutes: int = 60
    local_jwt_audience: str = "joyeria-local"

    # Supabase Auth (verificación de JWT emitido por Supabase vía JWKS).
    supabase_url: str = ""
    supabase_jwt_issuer: str = ""
    supabase_jwt_audience: str = "authenticated"
    supabase_service_role_key: str = ""

    # Los filtros por fecha representan dias comerciales en esta zona.
    business_timezone: str = "America/Mexico_City"

    # Persistencia local de imagenes de producto.
    product_media_root: Path = Path("media/products")
    product_media_url: str = "/media/products"
    product_image_max_bytes: int = 5 * 1024 * 1024
    product_image_max_pixels: int = 20_000_000

    @model_validator(mode="after")
    def validate_urls(self) -> Settings:
        if self.auth_provider not in {"supabase", "local"}:
            raise ValueError("AUTH_PROVIDER debe ser 'supabase' o 'local'")
        if self.database_url and not self.database_url.startswith(
            ("postgresql+asyncpg://", "sqlite+aiosqlite://")
        ):
            raise ValueError("DATABASE_URL debe usar un driver asincrono")
        if not self.product_media_url.startswith("/"):
            raise ValueError("PRODUCT_MEDIA_URL debe ser una ruta absoluta")
        if self.product_image_max_bytes <= 0 or self.product_image_max_pixels <= 0:
            raise ValueError("Los limites de imagen deben ser mayores que cero")
        try:
            ZoneInfo(self.business_timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("BUSINESS_TIMEZONE no es una zona horaria valida") from exc
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def auth_issuer(self) -> str:
        """Issuer canonico de Supabase Auth."""
        if self.supabase_jwt_issuer:
            return self.supabase_jwt_issuer.rstrip("/")
        if self.supabase_url:
            return f"{self.supabase_url.rstrip('/')}/auth/v1"
        return ""

    @property
    def jwks_url(self) -> str:
        """Endpoint JWKS de Supabase Auth."""
        return f"{self.auth_issuer}/.well-known/jwks.json" if self.auth_issuer else ""

    def validate_runtime(self) -> None:
        """Falla temprano en produccion si falta configuracion esencial."""
        if self.auth_provider == "local" and self.environment == "production":
            raise RuntimeError("AUTH_PROVIDER=local no esta permitido en produccion")
        if self.environment != "production":
            return
        missing = [
            name
            for name, value in (
                ("DATABASE_URL", self.database_url),
                ("SUPABASE_URL", self.supabase_url),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(f"Faltan variables requeridas: {', '.join(missing)}")


@lru_cache
def get_settings() -> Settings:
    return Settings()
