from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from jose import JWTError, jwt

from app.core.config import get_settings


class AuthError(Exception):
    def __init__(self, message: str = "No se pudo validar las credenciales") -> None:
        self.message = message
        super().__init__(message)


@dataclass(frozen=True)
class TokenClaims:
    """Claims mínimas del JWT emitido por Supabase Auth."""

    user_id: str
    email: str | None
    role: str | None  # rol del metadata; el rol canónico vive en user_profiles


_JWKS_TTL_SECONDS = 300.0
_ALLOWED_JWT_ALGORITHMS = {"RS256", "ES256"}
_LOCAL_ALGORITHM = "HS256"
_jwks_cache: dict | None = None
_jwks_cached_at: float = 0.0


def _reset_jwks_cache() -> None:
    global _jwks_cache, _jwks_cached_at
    _jwks_cache = None
    _jwks_cached_at = 0.0


async def get_jwks() -> dict:
    """Obtiene (y cachea brevemente) el JWKS de Supabase Auth."""
    global _jwks_cache, _jwks_cached_at
    if _jwks_cache is not None and (time.monotonic() - _jwks_cached_at) < _JWKS_TTL_SECONDS:
        return _jwks_cache

    settings = get_settings()
    if not settings.jwks_url:
        raise AuthError("SUPABASE_URL no esta configurado")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.jwks_url)
            resp.raise_for_status()
            payload = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise AuthError("No se pudo obtener la clave pública de autenticación") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
        raise AuthError("El servidor de autenticacion devolvio un JWKS invalido")

    _jwks_cache = payload
    _jwks_cached_at = time.monotonic()
    return payload


async def decode_access_token(token: str) -> TokenClaims:
    """Verifica el token segun el proveedor de auth configurado."""
    settings = get_settings()
    if settings.auth_provider == "local":
        return _decode_local_token(token)
    return await _decode_supabase_token(token, settings)


async def _decode_supabase_token(token: str, settings: Any) -> TokenClaims:
    """Verifica firma asimetrica, issuer y audience del JWT de Supabase."""
    try:
        header: dict[str, Any] = jwt.get_unverified_header(token)
        algorithm = header.get("alg")
        if algorithm not in _ALLOWED_JWT_ALGORITHMS:
            raise AuthError("Algoritmo de token no permitido")
        jwks = await get_jwks()
        claims = jwt.decode(
            token,
            jwks,
            algorithms=[algorithm],
            audience=settings.supabase_jwt_audience,
            issuer=settings.auth_issuer or None,
        )
    except AuthError:
        raise
    except JWTError as exc:
        raise AuthError("Token inválido o expirado") from exc

    subject = claims.get("sub")
    if not subject:
        raise AuthError("Token sin sujeto (sub)")

    app_metadata = claims.get("app_metadata") or {}
    role = app_metadata.get("role") or claims.get("user_role")
    return TokenClaims(user_id=str(subject), email=claims.get("email"), role=role)


def create_local_token(user_id: str, email: str | None, role: str | None) -> tuple[str, int]:
    """Emite un JWT HMAC (HS256) para el proveedor local. Solo desarrollo."""
    settings = get_settings()
    expire_seconds = settings.local_jwt_expire_minutes * 60
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "app_metadata": {"role": role},
        "aud": settings.local_jwt_audience,
        "iat": now,
        "exp": now + expire_seconds,
    }
    token = jwt.encode(payload, settings.local_jwt_secret, algorithm=_LOCAL_ALGORITHM)
    return token, expire_seconds


def _decode_local_token(token: str) -> TokenClaims:
    """Verifica un JWT HMAC emitido por create_local_token."""
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.local_jwt_secret,
            algorithms=[_LOCAL_ALGORITHM],
            audience=settings.local_jwt_audience,
        )
    except JWTError as exc:
        raise AuthError("Token inválido o expirado") from exc

    subject = claims.get("sub")
    if not subject:
        raise AuthError("Token sin sujeto (sub)")

    app_metadata = claims.get("app_metadata") or {}
    role = app_metadata.get("role")
    return TokenClaims(user_id=str(subject), email=claims.get("email"), role=role)
