"""
Pure domain entities for formulation intelligence.
Zero framework or database dependencies.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ScientificReferenceEntity:
    reference_id: str
    title: str
    authors: str
    journal: str
    year: int
    doi_or_url: str
    evidence_level: str  # e.g., 'clinical_trial', 'in_vitro', 'review', 'regulatory'
    summary: str


@dataclass(frozen=True)
class IngredientEntity:
    id: int
    name: str
    normalized_name: str
    function: str
    comedogenic: Optional[int] = None
    irritancy: Optional[int] = None
    is_pore_clogging: bool = False
    is_fungal_trigger: bool = False
    is_active: bool = False
    safety_class: str = "good"
    benefits: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class PersonaExclusionsEntity:
    fungal_acne_safe: bool = False
    fragrance_free: bool = False
    alcohol_free: bool = False
    oil_free: bool = False
    pore_clogger_free: bool = False
    custom_excluded_ingredients: List[str] = field(default_factory=list)


@dataclass
class SkinPersonaEntity:
    id: str
    username: str
    label: str
    skin_type: str = "combination"  # dry, oily, combination, normal
    sensitivity: str = "slightly_sensitive"  # not_sensitive, slightly_sensitive, very_sensitive
    target_concerns: List[str] = field(default_factory=list)
    exclusions: PersonaExclusionsEntity = field(default_factory=PersonaExclusionsEntity)


@dataclass(frozen=True)
class AspectObservationEntity:
    review_id: int
    aspect: str
    sentiment: str  # positive, negative, mixed, neutral
    negated: bool
    quote_span: str
    start: int
    end: int
    is_discovered: bool = False


@dataclass
class ReviewEntity:
    id: int
    product_id: int
    raw_text: str
    cleaned_text: str
    reviewer_skin_type: str = ""
    rating: float = 0.0
    date_posted: str = ""
    source: str = "nykaa"
    observations: List[AspectObservationEntity] = field(default_factory=list)


@dataclass
class ProductEntity:
    id: int
    brand: str
    name: str
    category: str = "moisturizer"
    price: float = 0.0
    price_tier: str = "$$"
    currency: str = "INR"
    size: str = ""
    rating: float = 0.0
    review_count: int = 0
    is_seed: bool = False
    formula_status: str = "unverified"  # verified, unverified, missing
    ingredients: List[str] = field(default_factory=list)
    normalized_ingredients: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
