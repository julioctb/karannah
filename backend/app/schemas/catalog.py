from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.catalog import ProductGroup, ProductStatus


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    group: ProductGroup
    requires_material: bool
    active: bool


class CategoryCreate(StrictModel):
    code: str = Field(min_length=1, max_length=4)
    name: str = Field(min_length=1, max_length=120)
    group: ProductGroup
    requires_material: bool = False


class CategoryUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    requires_material: bool | None = None
    active: bool | None = None


class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    active: bool


class MaterialCreate(StrictModel):
    code: str = Field(min_length=1, max_length=4)
    name: str = Field(min_length=1, max_length=120)


class MaterialUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    active: bool | None = None


class SubcategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    active: bool
    is_system: bool


class SubcategoryCreate(StrictModel):
    category_id: int
    name: str = Field(min_length=1, max_length=160)


class SubcategoryUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    active: bool | None = None


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    active: bool


class CollectionCreate(StrictModel):
    name: str = Field(min_length=1, max_length=120)


class CollectionUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    active: bool | None = None


class ProductVariantRead(BaseModel):
    id: int
    sku: str
    variant_value: str | None = None
    cost_price: Decimal | None = None
    retail_price: Decimal
    wholesale_price: Decimal
    active: bool


class ProductVariantCreate(StrictModel):
    variant_value: str | None = Field(default=None, max_length=80)
    cost_price: Decimal = Field(ge=0)
    retail_price: Decimal = Field(gt=0)
    wholesale_price: Decimal = Field(ge=0)


class ProductVariantUpdate(StrictModel):
    variant_value: str | None = Field(default=None, max_length=80)
    cost_price: Decimal | None = Field(default=None, ge=0)
    retail_price: Decimal | None = Field(default=None, gt=0)
    wholesale_price: Decimal | None = Field(default=None, ge=0)
    active: bool | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    category_id: int
    category_name: str
    material_id: int | None = None
    material_name: str | None = None
    subcategory_id: int | None = None
    subcategory_name: str | None = None
    stone: str | None = None
    status: ProductStatus
    notes: str | None = None
    image_url: str | None = None
    active: bool
    variant_type: str | None = None
    collection_ids: list[int] = []
    variants: list[ProductVariantRead]
    # Compatibilidad visual temporal: refleja la primera variante activa.
    sku: str
    cost_price: Decimal | None = None
    retail_price: Decimal
    wholesale_price: Decimal


class ProductCreate(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    category_id: int
    material_id: int | None = None
    subcategory_id: int | None = None
    stone: str | None = Field(default=None, max_length=160)
    status: ProductStatus = ProductStatus.DISPONIBLE
    notes: str | None = None
    variant_type: str | None = Field(default=None, max_length=40)
    collection_ids: list[int] = []
    variants: list[ProductVariantCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_variants(self) -> ProductCreate:
        values = [v.variant_value.strip() if v.variant_value else None for v in self.variants]
        if len(self.variants) > 1 and (
            not self.variant_type or any(value is None for value in values)
        ):
            raise ValueError("Las variantes multiples requieren tipo y valor")
        normalized = [value.casefold() for value in values if value]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Los valores de variante deben ser unicos")
        return self


class ProductUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category_id: int | None = None
    material_id: int | None = None
    subcategory_id: int | None = None
    stone: str | None = Field(default=None, max_length=160)
    status: ProductStatus | None = None
    notes: str | None = None
    variant_type: str | None = Field(default=None, max_length=40)
    collection_ids: list[int] | None = None
    active: bool | None = None
