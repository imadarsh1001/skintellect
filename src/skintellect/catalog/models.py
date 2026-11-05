"""
Pydantic Models & Schemas for FastAPI Backend
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PersonaExclusions(BaseModel):
    fungal_acne_safe: bool = False
    fragrance_free: bool = False
    alcohol_free: bool = False
    oil_free: bool = False
    pore_clogger_free: bool = False


class PersonaModel(BaseModel):
    id: str
    username: str
    label: str
    description: Optional[str] = ""
    skin_type: str = "combination"
    sensitivity: str = "slightly_sensitive"
    target_concerns: List[str] = Field(default_factory=list)
    safety_exclusions: PersonaExclusions = Field(default_factory=PersonaExclusions)
    is_default: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PersonaCreate(BaseModel):
    username: str
    label: str
    description: Optional[str] = ""
    skin_type: str = "combination"
    sensitivity: str = "slightly_sensitive"
    target_concerns: List[str] = Field(default_factory=list)
    safety_exclusions: PersonaExclusions = Field(default_factory=PersonaExclusions)


class ProductSummary(BaseModel):
    is_seed: bool = False
    formula_status: str = "unverified"
    score_kind: str = "heuristic_preference"
    id: int
    brand: str
    name: str
    slug: Optional[str] = ""
    url: Optional[str] = ""
    image_url: Optional[str] = ""
    category: Optional[str] = ""
    category_display: Optional[str] = ""
    domain: Optional[str] = "skin"
    target_area: Optional[str] = "face"
    brand_country: Optional[str] = ""
    price_tier: Optional[str] = "$$"
    price_range: Optional[str] = ""
    size: Optional[str] = ""
    routine_step: Optional[str] = ""
    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0
    match_score: int = 100
    composite_score: float = 0.0
    fungal_acne_safe: int = 0
    fragrance_free: int = 0
    alcohol_free: int = 0
    silicone_free: int = 0
    oil_free: int = 0
    pore_clogger_free: int = 0
    comedogenic_max: Optional[int] = 0
    irritancy_max: Optional[int] = 0
    has_detail: int = 0
    skin_goals: List[str] = Field(default_factory=list)
    community_survey: List[Dict[str, Any]] = Field(default_factory=list)
    analysis: Optional[Dict[str, Any]] = None
    match_reasons: List[str] = Field(default_factory=list)
    persona_match: Optional[Dict[str, Any]] = None


class PaginatedProductsResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    products: List[ProductSummary]
    active_persona: Optional[Dict[str, Any]] = None


class ProductDetail(ProductSummary):
    description: Optional[str] = ""
    badges: List[str] = Field(default_factory=list)
    ingredients: List[Dict[str, Any]] = Field(default_factory=list)
    key_actives: Any = Field(default_factory=list)
    key_benefits: Any = Field(default_factory=dict)
    rating_breakdown: Any = Field(default_factory=dict)
    reviews: List[Dict[str, Any]] = Field(default_factory=list)
    similar_products: List[Dict[str, Any]] = Field(default_factory=list)




















class CatalogStats(BaseModel):
    total_products: int
    enriched_products: int
    total_reviews: int
    total_ingredients: int
    category_counts: Dict[str, int]
    country_counts: Dict[str, int]
    price_tier_counts: Dict[str, int]


class IngredientSummary(BaseModel):
    id: int
    skinsort_id: Optional[int] = None
    name: str
    slug: str
    function: str
    description: Optional[str] = ""
    comedogenic: Optional[int] = None
    irritancy: Optional[int] = None
    is_pore_clogging: bool = False
    is_fungal_trigger: bool = False
    fungal_trigger_note: Optional[str] = ""
    is_active: bool = False
    category_badge: str
    safety_class: str
    benefits: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    product_count: int = 0


class PaginatedIngredientsResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    ingredients: List[IngredientSummary]


class IngredientFormulatingProduct(BaseModel):
    id: int
    brand: str
    name: str
    category: Optional[str] = ""
    price_tier: Optional[str] = ""
    image_url: Optional[str] = ""
    match_score: Optional[int] = 0
    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0
    is_key_ingredient: bool = False
    key_note: Optional[str] = ""


class IngredientDetail(IngredientSummary):
    formulating_products: List[IngredientFormulatingProduct] = Field(default_factory=list)
    total_products_count: int = 0
    source_profiles: Dict[str, Any] = Field(default_factory=dict)
