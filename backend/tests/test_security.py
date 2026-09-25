from __future__ import annotations

import base64
import time
import uuid

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from jose import jwt

from app.core import security
from app.core.config import Settings

AUDIENCE = "authenticated"


@pytest.fixture()
def rsa_keypair() -> tuple[bytes, dict]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    numbers = private_key.public_key().public_numbers()

    def b64int(n: int) -> str:
        raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    public_jwk = {
        "kty": "RSA",
        "kid": "test-key",
        "alg": "RS256",
        "use": "sig",
        "n": b64int(numbers.n),
        "e": b64int(numbers.e),
    }
    return private_pem, {"keys": [public_jwk]}


def make_token(key: bytes, sub: str, aud: str = AUDIENCE, **extra) -> str:
    now = int(time.time())
    claims = {"sub": sub, "aud": aud, "iat": now, "exp": now + 300}
    claims.update(extra)
    return jwt.encode(
        claims,
        key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )


@pytest.fixture()
def ec_keypair() -> tuple[bytes, dict]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    numbers = private_key.public_key().public_numbers()

    def b64coordinate(n: int) -> str:
        raw = n.to_bytes(32, "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    public_jwk = {
        "kty": "EC",
        "kid": "test-ec-key",
        "alg": "ES256",
        "use": "sig",
        "crv": "P-256",
        "x": b64coordinate(numbers.x),
        "y": b64coordinate(numbers.y),
    }
    return private_pem, {"keys": [public_jwk]}


@pytest.fixture()
def patch_jwks(monkeypatch, rsa_keypair):
    key, jwks = rsa_keypair
    security._reset_jwks_cache()

    async def fake_get_jwks() -> dict:
        return jwks

    monkeypatch.setattr(security, "get_jwks", fake_get_jwks)
    yield key
    security._reset_jwks_cache()


async def test_decode_valid_token(patch_jwks):
    uid = str(uuid.uuid4())
    token = make_token(patch_jwks, sub=uid, email="a@b.com", app_metadata={"role": "vendedor"})
    claims = await security.decode_access_token(token)
    assert claims.user_id == uid
    assert claims.email == "a@b.com"
    assert claims.role == "vendedor"


async def test_decode_rejects_bad_audience(patch_jwks):
    token = make_token(patch_jwks, sub=str(uuid.uuid4()), aud="anon")
    with pytest.raises(security.AuthError):
        await security.decode_access_token(token)


async def test_decode_rejects_bad_signature(patch_jwks):
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    token = make_token(other, sub=str(uuid.uuid4()))
    with pytest.raises(security.AuthError):
        await security.decode_access_token(token)


async def test_decode_rejects_expired(patch_jwks):
    now = int(time.time())
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "aud": AUDIENCE, "iat": now - 600, "exp": now - 300},
        patch_jwks,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )
    with pytest.raises(security.AuthError):
        await security.decode_access_token(token)


async def test_decode_valid_es256_token(monkeypatch, ec_keypair):
    key, jwks = ec_keypair

    async def fake_get_jwks() -> dict:
        return jwks

    monkeypatch.setattr(security, "get_jwks", fake_get_jwks)
    now = int(time.time())
    uid = str(uuid.uuid4())
    token = jwt.encode(
        {"sub": uid, "aud": AUDIENCE, "iat": now, "exp": now + 300},
        key,
        algorithm="ES256",
        headers={"kid": "test-ec-key"},
    )
    claims = await security.decode_access_token(token)
    assert claims.user_id == uid


async def test_decode_rejects_symmetric_algorithm(monkeypatch):
    now = int(time.time())
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "aud": AUDIENCE, "iat": now, "exp": now + 300},
        "a-secret-long-enough-for-testing",
        algorithm="HS256",
    )

    async def should_not_fetch_jwks() -> dict:
        raise AssertionError("JWKS should not be fetched for a rejected algorithm")

    monkeypatch.setattr(security, "get_jwks", should_not_fetch_jwks)
    with pytest.raises(security.AuthError, match="Algoritmo"):
        await security.decode_access_token(token)


@pytest.mark.parametrize(
    ("content", "content_type"),
    [(b"not-json", "text/plain"), (b'{"unexpected": []}', "application/json")],
)
async def test_get_jwks_rejects_invalid_response(monkeypatch, content, content_type):
    original_client = httpx.AsyncClient
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, content=content, headers={"content-type": content_type})
    )
    client = original_client(transport=transport)
    monkeypatch.setattr(
        security, "get_settings", lambda: Settings(supabase_url="https://example.com")
    )
    monkeypatch.setattr(security.httpx, "AsyncClient", lambda **_: client)
    security._reset_jwks_cache()

    with pytest.raises(security.AuthError):
        await security.get_jwks()
