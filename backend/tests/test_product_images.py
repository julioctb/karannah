from __future__ import annotations

import uuid
from io import BytesIO
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_claims
from app.core.db import Base, get_db
from app.core.security import TokenClaims
from app.main import app
from app.models.catalog import Category, Product, ProductGroup, ProductStatus, ProductVariant
from app.models.identity import Role, UserProfile
from app.services.product_images import (
    LocalProductImageStorage,
    ProductImageService,
    get_product_image_service,
)

ADMIN_ID = uuid.uuid4()
VENDEDOR_ID = uuid.uuid4()


def _image_bytes(image_format: str, size: tuple[int, int] = (5, 5)) -> bytes:
    output = BytesIO()
    Image.new("RGB", size, "#9b6a4f").save(output, format=image_format)
    return output.getvalue()


@pytest_asyncio.fixture()
async def image_client(tmp_path: Path):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add_all(
            [
                UserProfile(
                    id=ADMIN_ID,
                    email="admin-images@example.com",
                    full_name="Admin Images",
                    role=Role.ADMIN,
                ),
                UserProfile(
                    id=VENDEDOR_ID,
                    email="seller-images@example.com",
                    full_name="Seller Images",
                    role=Role.VENDEDOR,
                ),
                Category(
                    id=1,
                    code="AN",
                    name="Anillos",
                    group=ProductGroup.JOYERIA,
                    requires_material=False,
                ),
            ]
        )
        await session.flush()
        session.add(
            Product(
                id=1,
                name="Anillo para imagen",
                category_id=1,
                status=ProductStatus.DISPONIBLE,
            )
        )
        await session.flush()
        session.add(
            ProductVariant(
                id=1,
                product_id=1,
                sku="AN-IMG-0001",
                cost_price=100,
                retail_price=200,
                wholesale_price=150,
            )
        )
        await session.commit()

    storage = LocalProductImageStorage(tmp_path / "products")
    images = ProductImageService(storage=storage, max_bytes=1500, max_pixels=100)

    async def override_db():
        async with factory() as session:
            yield session

    def as_admin():
        return TokenClaims(user_id=str(ADMIN_ID), email="admin-images@example.com", role="admin")

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_claims] = as_admin
    app.dependency_overrides[get_product_image_service] = lambda: images
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, storage
    app.dependency_overrides.clear()
    await engine.dispose()


async def test_valid_upload_uses_actual_format_and_serializes_url(image_client) -> None:
    client, storage = image_client
    before = (await client.get("/api/v1/catalog/products/1")).json()
    assert before["image_url"] is None

    response = await client.put(
        "/api/v1/catalog/products/1/image",
        files={"file": ("not-really-text.txt", _image_bytes("PNG"), "text/plain")},
    )

    assert response.status_code == 200
    image_url = response.json()["image_url"]
    assert image_url.startswith("/media/products/")
    key = image_url.rsplit("/", 1)[-1]
    assert Path(key).suffix == ".png"
    uuid.UUID(Path(key).stem)
    stored = storage.root / key
    assert stored.is_file()
    with Image.open(stored) as normalized:
        assert normalized.format == "PNG"
        assert normalized.size == (5, 5)

    listed = (await client.get("/api/v1/catalog/products")).json()
    assert listed[0]["image_url"] == image_url


async def test_replacement_removes_previous_file(image_client) -> None:
    client, storage = image_client
    first = await client.put(
        "/api/v1/catalog/products/1/image",
        files={"file": ("first.png", _image_bytes("PNG"), "image/png")},
    )
    first_key = first.json()["image_url"].rsplit("/", 1)[-1]

    second = await client.put(
        "/api/v1/catalog/products/1/image",
        files={"file": ("second.png", _image_bytes("JPEG"), "image/png")},
    )

    assert second.status_code == 200
    second_key = second.json()["image_url"].rsplit("/", 1)[-1]
    assert second_key.endswith(".jpg")
    assert second_key != first_key
    assert not (storage.root / first_key).exists()
    assert (storage.root / second_key).is_file()


async def test_delete_is_idempotent_and_clears_serialization(image_client) -> None:
    client, storage = image_client
    await client.put(
        "/api/v1/catalog/products/1/image",
        files={"file": ("image.webp", _image_bytes("WEBP"), "image/webp")},
    )

    first = await client.delete("/api/v1/catalog/products/1/image")
    second = await client.delete("/api/v1/catalog/products/1/image")

    assert first.status_code == second.status_code == 204
    assert list(storage.root.iterdir()) == []
    product = (await client.get("/api/v1/catalog/products/1")).json()
    assert product["image_url"] is None


@pytest.mark.parametrize(
    ("name", "content", "content_type", "expected_status"),
    [
        ("spoofed.jpg", b"this is not a JPEG", "image/jpeg", 415),
        ("unsupported.gif", _image_bytes("GIF"), "image/gif", 415),
        ("too-large.jpg", b"x" * 1501, "image/jpeg", 413),
        ("too-many-pixels.png", _image_bytes("PNG", (11, 10)), "image/png", 413),
    ],
)
async def test_rejects_invalid_spoofed_and_oversized_images(
    image_client, name: str, content: bytes, content_type: str, expected_status: int
) -> None:
    client, storage = image_client
    response = await client.put(
        "/api/v1/catalog/products/1/image",
        files={"file": (name, content, content_type)},
    )
    assert response.status_code == expected_status
    assert list(storage.root.iterdir()) == []


async def test_vendedor_cannot_upload_or_delete_images(image_client) -> None:
    client, storage = image_client
    app.dependency_overrides[get_current_claims] = lambda: TokenClaims(
        user_id=str(VENDEDOR_ID), email="seller-images@example.com", role="vendedor"
    )

    uploaded = await client.put(
        "/api/v1/catalog/products/1/image",
        files={"file": ("image.png", _image_bytes("PNG"), "image/png")},
    )
    deleted = await client.delete("/api/v1/catalog/products/1/image")

    assert uploaded.status_code == deleted.status_code == 403
    assert list(storage.root.iterdir()) == []


def test_local_storage_rejects_path_traversal_and_delete_is_idempotent(tmp_path: Path) -> None:
    storage = LocalProductImageStorage(tmp_path / "products")
    with pytest.raises(ValueError, match="Clave de imagen"):
        storage.delete("../outside.jpg")

    key = storage.write(b"normalized", ".jpg")
    storage.delete(key)
    storage.delete(key)
    assert not (storage.root / key).exists()


def test_local_storage_deletes_only_unreferenced_files(tmp_path: Path) -> None:
    storage = LocalProductImageStorage(tmp_path / "products")
    retained = storage.write(b"retained", ".png")
    orphan = storage.write(b"orphan", ".webp")

    storage.delete_unreferenced({retained})

    assert (storage.root / retained).is_file()
    assert not (storage.root / orphan).exists()
