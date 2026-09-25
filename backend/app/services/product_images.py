from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Protocol

from fastapi import Request
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import Settings, get_settings

_FORMAT_SUFFIXES = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


class InvalidProductImage(ValueError):
    pass


class ProductImageTooLarge(ValueError):
    pass


class ProductImageStorage(Protocol):
    def write(self, content: bytes, suffix: str) -> str: ...

    def delete(self, key: str) -> None: ...

    def delete_unreferenced(self, referenced_keys: set[str]) -> None: ...


class LocalProductImageStorage:
    def __init__(self, root: Path) -> None:
        root.mkdir(parents=True, exist_ok=True)
        self.root = root.resolve()

    def _path_for(self, key: str) -> Path:
        candidate = Path(key)
        if candidate.name != key or candidate.suffix not in _FORMAT_SUFFIXES.values():
            raise ValueError("Clave de imagen local invalida")
        try:
            parsed = uuid.UUID(candidate.stem)
        except ValueError as exc:
            raise ValueError("Clave de imagen local invalida") from exc
        if str(parsed) != candidate.stem:
            raise ValueError("Clave de imagen local invalida")
        resolved = (self.root / candidate).resolve()
        if not resolved.is_relative_to(self.root):
            raise ValueError("La clave de imagen sale del directorio configurado")
        return resolved

    def write(self, content: bytes, suffix: str) -> str:
        if suffix not in _FORMAT_SUFFIXES.values():
            raise ValueError("Extension de imagen no permitida")
        key = f"{uuid.uuid4()}{suffix}"
        target = self._path_for(key)
        temporary = self.root / f".{uuid.uuid4()}.tmp"
        try:
            with temporary.open("xb") as output:
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return key

    def delete(self, key: str) -> None:
        self._path_for(key).unlink(missing_ok=True)

    def delete_unreferenced(self, referenced_keys: set[str]) -> None:
        for path in self.root.iterdir():
            if path.is_file() and path.name not in referenced_keys:
                path.unlink(missing_ok=True)


@dataclass(frozen=True)
class ProductImageService:
    storage: ProductImageStorage
    max_bytes: int
    max_pixels: int

    def save(self, content: bytes) -> str:
        if len(content) > self.max_bytes:
            raise ProductImageTooLarge("La imagen excede el limite de bytes")
        normalized, suffix = self._normalize(content)
        if len(normalized) > self.max_bytes:
            raise ProductImageTooLarge("La imagen normalizada excede el limite de bytes")
        return self.storage.write(normalized, suffix)

    def delete(self, key: str) -> None:
        self.storage.delete(key)

    def delete_unreferenced(self, referenced_keys: set[str]) -> None:
        self.storage.delete_unreferenced(referenced_keys)

    def _normalize(self, content: bytes) -> tuple[bytes, str]:
        try:
            with Image.open(BytesIO(content)) as source:
                image_format = source.format
                if image_format not in _FORMAT_SUFFIXES:
                    raise InvalidProductImage("Solo se aceptan imagenes JPEG, PNG o WebP")
                if source.width * source.height > self.max_pixels:
                    raise ProductImageTooLarge("La imagen excede el limite de pixeles")
                source.verify()

            with Image.open(BytesIO(content)) as source:
                source.seek(0)
                normalized = ImageOps.exif_transpose(source)
                has_alpha = "A" in normalized.getbands() or "transparency" in normalized.info
                normalized = normalized.convert("RGBA" if has_alpha else "RGB")
                normalized.load()
                output = BytesIO()
                if image_format == "JPEG":
                    normalized.convert("RGB").save(
                        output, format="JPEG", quality=85, optimize=True, progressive=True
                    )
                elif image_format == "PNG":
                    normalized.save(output, format="PNG", optimize=True)
                else:
                    normalized.save(output, format="WEBP", quality=85, method=6)
        except ProductImageTooLarge:
            raise
        except InvalidProductImage:
            raise
        except (Image.DecompressionBombError, UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidProductImage("El archivo no es una imagen valida") from exc
        return output.getvalue(), _FORMAT_SUFFIXES[image_format]


def build_product_image_service(settings: Settings | None = None) -> ProductImageService:
    settings = settings or get_settings()
    return ProductImageService(
        storage=LocalProductImageStorage(settings.product_media_root),
        max_bytes=settings.product_image_max_bytes,
        max_pixels=settings.product_image_max_pixels,
    )


def get_product_image_service(request: Request) -> ProductImageService:
    return request.app.state.product_image_service


def product_image_url(key: str) -> str:
    return f"{get_settings().product_media_url.rstrip('/')}/{key}"
