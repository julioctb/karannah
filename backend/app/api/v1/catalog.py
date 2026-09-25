from __future__ import annotations

import logging
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import ensure_role, get_current_profile
from app.api.pagination import PaginationParams
from app.core.db import get_db
from app.models.catalog import (
    Category,
    Collection,
    Material,
    Product,
    ProductCollection,
    ProductStatus,
    ProductVariant,
    SkuCounter,
    Subcategory,
)
from app.models.identity import Role, UserProfile
from app.schemas.catalog import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CollectionCreate,
    CollectionRead,
    CollectionUpdate,
    MaterialCreate,
    MaterialRead,
    MaterialUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantRead,
    ProductVariantUpdate,
    SubcategoryCreate,
    SubcategoryRead,
    SubcategoryUpdate,
)
from app.services.product_images import (
    InvalidProductImage,
    ProductImageService,
    ProductImageTooLarge,
    get_product_image_service,
    product_image_url,
)
from app.services.sku import allocate_skus

router = APIRouter(prefix="/catalog", tags=["catalog"])
logger = logging.getLogger(__name__)

Db = Annotated[AsyncSession, Depends(get_db)]
Profile = Annotated[UserProfile, Depends(get_current_profile)]
ImageService = Annotated[ProductImageService, Depends(get_product_image_service)]


async def _commit(db: AsyncSession, conflict: str) -> None:
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail=conflict) from exc


async def _active_category(db: AsyncSession, category_id: int) -> Category:
    row = await db.get(Category, category_id)
    if row is None or not row.active:
        raise HTTPException(status_code=422, detail="Categoria inexistente o inactiva")
    return row


async def _product_references(
    db: AsyncSession,
    category_id: int,
    material_id: int | None,
    subcategory_id: int | None,
    collection_ids: list[int],
) -> tuple[Category, Material | None, Subcategory | None, list[Collection]]:
    category = await _active_category(db, category_id)
    material = await db.get(Material, material_id) if material_id is not None else None
    if category.requires_material and (material is None or not material.active):
        raise HTTPException(status_code=422, detail="La categoria requiere un material activo")
    if material_id is not None and (material is None or not material.active):
        raise HTTPException(status_code=422, detail="Material inexistente o inactivo")

    subcategory = await db.get(Subcategory, subcategory_id) if subcategory_id else None
    if subcategory_id and (
        subcategory is None or not subcategory.active or subcategory.category_id != category.id
    ):
        raise HTTPException(status_code=422, detail="Subcategoria invalida para la categoria")

    unique_ids = list(dict.fromkeys(collection_ids))
    collections = (
        list(
            (
                await db.scalars(
                    select(Collection).where(
                        Collection.id.in_(unique_ids), Collection.active.is_(True)
                    )
                )
            ).all()
        )
        if unique_ids
        else []
    )
    if len(collections) != len(unique_ids):
        raise HTTPException(status_code=422, detail="Coleccion inexistente o inactiva")
    return category, material, subcategory, collections


async def _read_products(
    db: AsyncSession,
    profile: UserProfile,
    stmt,  # type: ignore[no-untyped-def]
    include_inactive: bool,
) -> list[ProductRead]:
    rows = (await db.execute(stmt)).all()
    if not rows:
        return []
    ids = [row[0].id for row in rows]
    variant_stmt = select(ProductVariant).where(ProductVariant.product_id.in_(ids))
    if not include_inactive:
        variant_stmt = variant_stmt.where(ProductVariant.active.is_(True))
    variants = (await db.scalars(variant_stmt.order_by(ProductVariant.id))).all()
    by_product: dict[int, list[ProductVariant]] = defaultdict(list)
    for variant in variants:
        by_product[variant.product_id].append(variant)
    collection_rows = (
        await db.execute(
            select(ProductCollection.product_id, ProductCollection.collection_id).where(
                ProductCollection.product_id.in_(ids)
            )
        )
    ).all()
    collection_ids: dict[int, list[int]] = defaultdict(list)
    for product_id, collection_id in collection_rows:
        collection_ids[product_id].append(collection_id)

    is_admin = profile.role is Role.ADMIN
    result: list[ProductRead] = []
    for product, category_name, material_name, subcategory_name in rows:
        product_variants = by_product[product.id]
        if not product_variants:
            continue
        serialized = [
            ProductVariantRead(
                id=v.id,
                sku=v.sku,
                variant_value=v.variant_value,
                cost_price=v.cost_price if is_admin else None,
                retail_price=v.retail_price,
                wholesale_price=v.wholesale_price,
                active=v.active,
            )
            for v in product_variants
        ]
        primary = serialized[0]
        result.append(
            ProductRead(
                id=product.id,
                name=product.name,
                category_id=product.category_id,
                category_name=category_name,
                material_id=product.material_id,
                material_name=material_name,
                subcategory_id=product.subcategory_id,
                subcategory_name=subcategory_name,
                stone=product.stone,
                status=product.status,
                notes=product.notes,
                image_url=product_image_url(product.image_key) if product.image_key else None,
                active=product.active,
                variant_type=product.variant_type,
                collection_ids=collection_ids[product.id],
                variants=serialized,
                sku=primary.sku,
                cost_price=primary.cost_price,
                retail_price=primary.retail_price,
                wholesale_price=primary.wholesale_price,
            )
        )
    return result


def _product_stmt():  # type: ignore[no-untyped-def]
    return (
        select(Product, Category.name, Material.name, Subcategory.name)
        .join(Category, Category.id == Product.category_id)
        .outerjoin(Material, Material.id == Product.material_id)
        .outerjoin(Subcategory, Subcategory.id == Product.subcategory_id)
        .order_by(Product.id)
    )


@router.get("/categories", response_model=list[CategoryRead])
async def list_categories(
    db: Db, _profile: Profile, include_inactive: bool = False
) -> list[CategoryRead]:
    stmt = select(Category).order_by(Category.code)
    if not include_inactive:
        stmt = stmt.where(Category.active.is_(True))
    return list((await db.scalars(stmt)).all())


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, db: Db, profile: Profile) -> Category:
    ensure_role(profile, Role.ADMIN)
    row = Category(
        code=payload.code.strip().upper(),
        name=payload.name.strip(),
        group=payload.group,
        requires_material=payload.requires_material,
    )
    db.add(row)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="La clave de categoria ya existe") from exc
    db.add(SkuCounter(category_id=row.id, next_value=1))
    await _commit(db, "La clave o nombre de categoria ya existe")
    await db.refresh(row)
    return row


@router.patch("/categories/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int, payload: CategoryUpdate, db: Db, profile: Profile
) -> Category:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Category, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value.strip() if isinstance(value, str) else value)
    await _commit(db, "La categoria entra en conflicto con otra existente")
    await db.refresh(row)
    return row


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_category(category_id: int, db: Db, profile: Profile) -> Response:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Category, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    row.active = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/materials", response_model=list[MaterialRead])
async def list_materials(
    db: Db, _profile: Profile, include_inactive: bool = False
) -> list[MaterialRead]:
    stmt = select(Material).order_by(Material.code)
    if not include_inactive:
        stmt = stmt.where(Material.active.is_(True))
    return list((await db.scalars(stmt)).all())


@router.post("/materials", response_model=MaterialRead, status_code=status.HTTP_201_CREATED)
async def create_material(payload: MaterialCreate, db: Db, profile: Profile) -> Material:
    ensure_role(profile, Role.ADMIN)
    row = Material(code=payload.code.strip().upper(), name=payload.name.strip())
    db.add(row)
    await _commit(db, "La clave o nombre de material ya existe")
    await db.refresh(row)
    return row


@router.patch("/materials/{material_id}", response_model=MaterialRead)
async def update_material(
    material_id: int, payload: MaterialUpdate, db: Db, profile: Profile
) -> Material:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Material, material_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value.strip() if isinstance(value, str) else value)
    await _commit(db, "El material entra en conflicto con otro existente")
    await db.refresh(row)
    return row


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_material(material_id: int, db: Db, profile: Profile) -> Response:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Material, material_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    row.active = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/subcategories", response_model=list[SubcategoryRead])
async def list_subcategories(
    db: Db,
    _profile: Profile,
    category_id: Annotated[int | None, Query()] = None,
    include_inactive: bool = False,
) -> list[SubcategoryRead]:
    stmt = select(Subcategory).order_by(Subcategory.name)
    if category_id is not None:
        stmt = stmt.where(Subcategory.category_id == category_id)
    if not include_inactive:
        stmt = stmt.where(Subcategory.active.is_(True))
    return list((await db.scalars(stmt)).all())


@router.post("/subcategories", response_model=SubcategoryRead, status_code=status.HTTP_201_CREATED)
async def create_subcategory(payload: SubcategoryCreate, db: Db, profile: Profile) -> Subcategory:
    ensure_role(profile, Role.ADMIN)
    await _active_category(db, payload.category_id)
    row = Subcategory(category_id=payload.category_id, name=payload.name.strip())
    db.add(row)
    await _commit(db, "La subcategoria ya existe en esta categoria")
    await db.refresh(row)
    return row


@router.patch("/subcategories/{subcategory_id}", response_model=SubcategoryRead)
async def update_subcategory(
    subcategory_id: int, payload: SubcategoryUpdate, db: Db, profile: Profile
) -> Subcategory:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Subcategory, subcategory_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Subcategoria no encontrada")
    if row.is_system and payload.active is False:
        raise HTTPException(status_code=409, detail="Una subcategoria del sistema no se desactiva")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value.strip() if isinstance(value, str) else value)
    await _commit(db, "La subcategoria ya existe en esta categoria")
    await db.refresh(row)
    return row


@router.delete("/subcategories/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_subcategory(subcategory_id: int, db: Db, profile: Profile) -> Response:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Subcategory, subcategory_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Subcategoria no encontrada")
    if row.is_system:
        raise HTTPException(status_code=409, detail="Una subcategoria del sistema no se desactiva")
    row.active = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/collections", response_model=list[CollectionRead])
async def list_collections(
    db: Db, _profile: Profile, include_inactive: bool = False
) -> list[CollectionRead]:
    stmt = select(Collection).order_by(Collection.name)
    if not include_inactive:
        stmt = stmt.where(Collection.active.is_(True))
    return list((await db.scalars(stmt)).all())


@router.post("/collections", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_collection(payload: CollectionCreate, db: Db, profile: Profile) -> Collection:
    ensure_role(profile, Role.ADMIN)
    row = Collection(name=payload.name.strip())
    db.add(row)
    await _commit(db, "La coleccion ya existe")
    await db.refresh(row)
    return row


@router.patch("/collections/{collection_id}", response_model=CollectionRead)
async def update_collection(
    collection_id: int, payload: CollectionUpdate, db: Db, profile: Profile
) -> Collection:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Collection, collection_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Coleccion no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value.strip() if isinstance(value, str) else value)
    await _commit(db, "La coleccion ya existe")
    await db.refresh(row)
    return row


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_collection(collection_id: int, db: Db, profile: Profile) -> Response:
    ensure_role(profile, Role.ADMIN)
    row = await db.get(Collection, collection_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Coleccion no encontrada")
    row.active = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    db: Db,
    profile: Profile,
    page: PaginationParams,
    search: Annotated[str | None, Query(max_length=120)] = None,
    category_id: Annotated[int | None, Query()] = None,
    material_id: Annotated[int | None, Query()] = None,
    status_filter: Annotated[ProductStatus | None, Query(alias="status")] = None,
    include_inactive: bool = False,
) -> list[ProductRead]:
    limit, offset = page
    stmt = _product_stmt()
    if not include_inactive:
        stmt = stmt.where(Product.active.is_(True))
    if search:
        like = f"%{search}%"
        matching_products = select(ProductVariant.product_id).where(
            or_(ProductVariant.sku.ilike(like), ProductVariant.variant_value.ilike(like))
        )
        stmt = stmt.where(or_(Product.name.ilike(like), Product.id.in_(matching_products)))
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if material_id is not None:
        stmt = stmt.where(Product.material_id == material_id)
    if status_filter is not None:
        stmt = stmt.where(Product.status == status_filter)
    return await _read_products(db, profile, stmt.limit(limit).offset(offset), include_inactive)


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: Db, profile: Profile) -> ProductRead:
    rows = await _read_products(db, profile, _product_stmt().where(Product.id == product_id), True)
    if not rows:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return rows[0]


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db: Db, profile: Profile) -> ProductRead:
    ensure_role(profile, Role.ADMIN)
    category, material, _subcategory, collections = await _product_references(
        db,
        payload.category_id,
        payload.material_id,
        payload.subcategory_id,
        payload.collection_ids,
    )
    product = Product(
        name=payload.name.strip(),
        category_id=category.id,
        material_id=material.id if material else None,
        subcategory_id=payload.subcategory_id,
        stone=payload.stone.strip() if payload.stone else None,
        status=payload.status,
        notes=payload.notes,
        variant_type=payload.variant_type.strip() if payload.variant_type else None,
    )
    db.add(product)
    await db.flush()
    skus = await allocate_skus(db, category, material, len(payload.variants))
    for sku, variant in zip(skus, payload.variants, strict=True):
        db.add(
            ProductVariant(
                product_id=product.id,
                sku=sku,
                variant_value=variant.variant_value.strip() if variant.variant_value else None,
                cost_price=variant.cost_price,
                retail_price=variant.retail_price,
                wholesale_price=variant.wholesale_price,
            )
        )
    for collection in collections:
        db.add(ProductCollection(product_id=product.id, collection_id=collection.id))
    await _commit(db, "No se pudo crear el producto por un conflicto de SKU o variante")
    return await get_product(product.id, db, profile)


@router.patch("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int, payload: ProductUpdate, db: Db, profile: Profile
) -> ProductRead:
    ensure_role(profile, Role.ADMIN)
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    was_active = product.active
    data = payload.model_dump(exclude_unset=True)
    category_id = data.get("category_id", product.category_id)
    material_id = data.get("material_id", product.material_id)
    subcategory_id = data.get("subcategory_id", product.subcategory_id)
    requested_collections = data.get("collection_ids")
    existing_collection_ids = list(
        await db.scalars(
            select(ProductCollection.collection_id).where(
                ProductCollection.product_id == product.id
            )
        )
    )
    _, _, _, collections = await _product_references(
        db,
        category_id,
        material_id,
        subcategory_id,
        requested_collections if requested_collections is not None else existing_collection_ids,
    )
    for field in (
        "name",
        "category_id",
        "material_id",
        "subcategory_id",
        "stone",
        "status",
        "notes",
        "variant_type",
        "active",
    ):
        if field in data:
            value = data[field]
            setattr(product, field, value.strip() if isinstance(value, str) else value)
    if "active" in data and product.active != was_active:
        variants = await db.scalars(
            select(ProductVariant).where(ProductVariant.product_id == product.id)
        )
        for variant in variants:
            variant.active = product.active
    if requested_collections is not None:
        await db.execute(
            delete(ProductCollection).where(ProductCollection.product_id == product.id)
        )
        for collection in collections:
            db.add(ProductCollection(product_id=product.id, collection_id=collection.id))
    await _commit(db, "No se pudo actualizar el producto")
    return await get_product(product.id, db, profile)


@router.put("/products/{product_id}/image", response_model=ProductRead)
async def replace_product_image(
    product_id: int,
    file: Annotated[UploadFile, File()],
    db: Db,
    profile: Profile,
    images: ImageService,
) -> ProductRead:
    ensure_role(profile, Role.ADMIN)
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    try:
        content = await file.read(images.max_bytes + 1)
    finally:
        await file.close()
    if len(content) > images.max_bytes:
        raise HTTPException(status_code=413, detail="La imagen excede el limite de bytes")
    try:
        new_key = await run_in_threadpool(images.save, content)
    except ProductImageTooLarge as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except InvalidProductImage as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    old_key = product.image_key
    product.image_key = new_key
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        await run_in_threadpool(images.delete, new_key)
        raise

    if old_key:
        try:
            await run_in_threadpool(images.delete, old_key)
        except OSError:
            logger.exception("No se pudo eliminar la imagen reemplazada %s", old_key)
    return await get_product(product.id, db, profile)


@router.delete("/products/{product_id}/image", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    product_id: int, db: Db, profile: Profile, images: ImageService
) -> Response:
    ensure_role(profile, Role.ADMIN)
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    old_key = product.image_key
    if old_key is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    product.image_key = None
    await db.commit()
    try:
        await run_in_threadpool(images.delete, old_key)
    except OSError:
        logger.exception("No se pudo eliminar la imagen de producto %s", old_key)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/products/{product_id}/variants",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_product_variant(
    product_id: int, payload: ProductVariantCreate, db: Db, profile: Profile
) -> ProductRead:
    ensure_role(profile, Role.ADMIN)
    product = await db.get(Product, product_id)
    if product is None or not product.active:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not product.variant_type or not payload.variant_value:
        raise HTTPException(status_code=422, detail="El producto no admite variantes adicionales")
    category = await _active_category(db, product.category_id)
    material = await db.get(Material, product.material_id) if product.material_id else None
    sku = (await allocate_skus(db, category, material, 1))[0]
    db.add(
        ProductVariant(
            product_id=product.id,
            sku=sku,
            variant_value=payload.variant_value.strip(),
            cost_price=payload.cost_price,
            retail_price=payload.retail_price,
            wholesale_price=payload.wholesale_price,
        )
    )
    await _commit(db, "El valor de variante ya existe")
    return await get_product(product.id, db, profile)


@router.patch("/products/{product_id}/variants/{variant_id}", response_model=ProductRead)
async def update_product_variant(
    product_id: int,
    variant_id: int,
    payload: ProductVariantUpdate,
    db: Db,
    profile: Profile,
) -> ProductRead:
    ensure_role(profile, Role.ADMIN)
    variant = await db.get(ProductVariant, variant_id)
    if variant is None or variant.product_id != product_id:
        raise HTTPException(status_code=404, detail="Variante no encontrada")
    data = payload.model_dump(exclude_unset=True)
    if "active" in data:
        product = await db.get(Product, product_id)
        if data["active"] is True and product is not None and not product.active:
            raise HTTPException(
                status_code=409,
                detail="No se puede activar una variante de un producto inactivo",
            )
        if data["active"] is False and variant.active:
            active_count = await db.scalar(
                select(func.count())
                .select_from(ProductVariant)
                .where(
                    ProductVariant.product_id == product_id,
                    ProductVariant.active.is_(True),
                )
            )
            if int(active_count or 0) <= 1:
                raise HTTPException(
                    status_code=409,
                    detail="El producto debe conservar al menos una variante activa",
                )
    for field, value in data.items():
        setattr(variant, field, value.strip() if isinstance(value, str) else value)
    await _commit(db, "El valor de variante ya existe")
    return await get_product(product_id, db, profile)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_product(product_id: int, db: Db, profile: Profile) -> Response:
    ensure_role(profile, Role.ADMIN)
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    product.active = False
    variants = await db.scalars(
        select(ProductVariant).where(ProductVariant.product_id == product.id)
    )
    for variant in variants:
        variant.active = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
