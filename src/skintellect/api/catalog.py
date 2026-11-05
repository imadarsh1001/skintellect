from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

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
from skintellect.catalog.products import get_catalog_stats, get_product_by_id, get_products
from skintellect.catalog.taxonomy import get_all_domains, get_all_sources

router = APIRouter()

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
