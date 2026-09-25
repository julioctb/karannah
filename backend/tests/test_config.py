from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_supabase_auth_urls_are_derived_from_project_url() -> None:
    settings = Settings(supabase_url="https://example.supabase.co")
    assert settings.auth_issuer == "https://example.supabase.co/auth/v1"
    assert settings.jwks_url == "https://example.supabase.co/auth/v1/.well-known/jwks.json"


def test_explicit_issuer_takes_precedence() -> None:
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_jwt_issuer="https://auth.example.com/issuer/",
    )
    assert settings.auth_issuer == "https://auth.example.com/issuer"


def test_rejects_synchronous_database_driver() -> None:
    with pytest.raises(ValidationError, match="driver asincrono"):
        Settings(database_url="postgresql://postgres:secret@localhost/db")


def test_production_requires_database_and_supabase() -> None:
    settings = Settings(environment="production")
    with pytest.raises(RuntimeError, match="DATABASE_URL, SUPABASE_URL"):
        settings.validate_runtime()


def test_rejects_unknown_business_timezone() -> None:
    with pytest.raises(ValidationError, match="BUSINESS_TIMEZONE"):
        Settings(business_timezone="Mars/Olympus")
