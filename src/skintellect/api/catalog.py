from typing import List, Optional

import os
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from skintellect import config
from skintellect.catalog.ingredients import (
    get_ingredient_detail,
    get_ingredient_functions,
    get_ingredients,
)
from skintellect.catalog.models import (
    CatalogStats,
    IngredientDetail,
    PaginatedIngredientsResponse,
    PaginatedProductsResponse,
    PersonaCreate,
    PersonaModel,
    ProductDetail,
)
from skintellect.catalog.personas import get_all_personas, save_persona
from skintellect.catalog.products import get_catalog_stats, get_product_by_id, get_product_image_url, get_products
from skintellect.catalog.taxonomy import get_all_domains, get_all_sources

router = APIRouter()

# The image proxy only ever fetches from the collector's object storage
# (SSRF guard); anything else in the data is rejected before a request
# leaves the process.
IMAGE_ALLOWED_HOSTS = {"storage.skinsort.com"}
IMAGE_FETCH_TIMEOUT = 20.0

@router.get("/api/products", response_model=PaginatedProductsResponse)
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(36, ge=1, le=100),
    category: str = Query("all"),
    domain: str = Query("all"),
    price_tier: str = Query("all"),
    country: str = Query("all"),
    goal: str = Query("all"),
    min_match: int = Query(0, ge=0, le=100),
    search: str = Query(""),
    fungal_safe: bool = Query(False),
    fragrance_free: bool = Query(False),
    oil_free: bool = Query(False),
    pore_free: bool = Query(False),
    sort_by: str = Query("composite_desc"),
    persona_id: str = Query("uap"),
    include_seeds: bool = Query(False, description="Include explicitly labeled demonstration seed records")
):
    """Returns paginated, dynamically scored skincare products."""
    return get_products(
        page=page,
        limit=limit,
        category=category,
        domain=domain,
        price_tier=price_tier,
        country=country,
        goal=goal,
        min_match=min_match,
        search=search,
        fungal_safe=fungal_safe,
        fragrance_free=fragrance_free,
        oil_free=oil_free,
        pore_free=pore_free,
        sort_by=sort_by,
        persona_id=persona_id,
        include_seeds=include_seeds
    )

@router.get("/api/products/{product_id}", response_model=ProductDetail)
def get_product_details(product_id: int, persona_id: str = Query("uap")):
    """Returns deep details, ingredients, reviews, and clinical scoring for a single product."""
    product = get_product_by_id(product_id, persona_id=persona_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def _image_url_allowed(url: str) -> bool:
    """SSRF guard: https on the collector's object-storage host, nothing else."""
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in IMAGE_ALLOWED_HOSTS


def _sniff_image_type(data: bytes) -> str:
    if data.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"GIF8"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


def _fetch_image_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "skintellect-image-proxy/1.0"})
    with urllib.request.urlopen(request, timeout=IMAGE_FETCH_TIMEOUT) as response:
        data = response.read()
    if not data or _sniff_image_type(data) == "application/octet-stream":
        raise ValueError("response is not a recognised image")
    return data


@router.get("/api/products/{product_id}/image")
def get_product_image(product_id: int):
    """Serves a product's scraped source image through the backend, caching on disk.

    The scraped image_url points at the collector's object storage; the UI never
    hotlinks it. The first request fetches the bytes and caches them under
    IMAGE_CACHE_DIR; later requests serve straight from disk. Outbound hosts are
    allowlisted, and the cached bytes are served with their sniffed media type.
    Sync endpoints run on a threadpool, so concurrent first fetches write to
    distinct temp files and the final os.replace wins atomically.
    """
    image_url = get_product_image_url(product_id)
    if not image_url:
        raise HTTPException(status_code=404, detail="Product has no source image")
    if not _image_url_allowed(image_url):
        raise HTTPException(status_code=400, detail="Image host not allowed")

    cache_dir = Path(config.IMAGE_CACHE_DIR)
    cache_path = cache_dir / str(product_id)
    if cache_path.exists():
        data = cache_path.read_bytes()
        return Response(content=data, media_type=_sniff_image_type(data))

    try:
        data = _fetch_image_bytes(image_url)
    except Exception as exc:  # noqa: BLE001 - any network failure is an upstream failure
        print(f"[image-proxy] product {product_id} fetch failed: {exc}")
        raise HTTPException(status_code=502, detail="Image fetch failed") from exc

    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = cache_dir / f".{product_id}.{os.getpid()}.tmp"
    tmp_path.write_bytes(data)
    os.replace(tmp_path, cache_path)

    return Response(content=data, media_type=_sniff_image_type(data))

@router.get("/api/domains")
def list_domains():
    """Returns supported cosmetic & body care domains (Skin, Hair, Body, Makeup)."""
    return {"domains": get_all_domains()}

@router.get("/api/sources")
def list_sources():
    """Returns multi-source intelligence registries (Skintellect, INCIDecoder, CIR, PubChem)."""
    return {"sources": [s | {"status": "configured_registry", "verified": False}
                        for s in get_all_sources()]}

@router.get("/api/ingredients", response_model=PaginatedIngredientsResponse)
def list_ingredients(
    search: str = Query(""),
    function: str = Query("all"),
    domain: str = Query("all"),
    comedogenic_max: Optional[int] = Query(None, ge=0, le=5),
    fungal_safe_only: bool = Query(False),
    active_only: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100)
):
    """Searches, filters, and paginates the 1,490+ ingredient registry."""
    return get_ingredients(
        search=search,
        function=function,
        domain=domain,
        comedogenic_max=comedogenic_max,
        fungal_safe_only=fungal_safe_only,
        active_only=active_only,
        page=page,
        limit=limit
    )

@router.get("/api/ingredients/meta/functions")
def list_ingredient_functions():
    """Returns unique cosmetic functions across indexed ingredients for dropdown filtering."""
    return {"functions": get_ingredient_functions()}

@router.get("/api/ingredients/{ingredient_id}", response_model=IngredientDetail)
def get_single_ingredient(ingredient_id: str):
    """Retrieves deep scientific dossier for an ingredient including products formulated with it."""
    detail = get_ingredient_detail(ingredient_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Ingredient '{ingredient_id}' not found")
    return detail

@router.get("/api/personas", response_model=List[PersonaModel])
def list_personas():
    """Lists all stored personas (uap is default)."""
    return get_all_personas()

@router.post("/api/personas", response_model=PersonaModel)
def create_persona(payload: PersonaCreate):
    """Persist a custom persona through the catalog module."""
    try:
        return save_persona(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from None

@router.get("/api/personas/{persona_id}", response_model=PersonaModel)
def get_persona_detail(persona_id: str):
    """Retrieves a specific persona by ID or username."""
    personas = get_all_personas()
    p = next((x for x in personas if x["id"] == persona_id or x["username"] == persona_id), None)
    if not p:
        raise HTTPException(status_code=404, detail="Persona not found")
    return p

@router.get("/api/stats", response_model=CatalogStats)
def catalog_stats():
    """Returns catalog metrics and distribution counts."""
    return get_catalog_stats()
