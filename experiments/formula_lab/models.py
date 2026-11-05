"""Formula and routine request/response validation contracts."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from skintellect.catalog.models import ProductSummary


class RoutineAnalyzeRequest(BaseModel):
    product_ids: List[int]
    persona_id: Optional[str] = "uap"


class ConflictItem(BaseModel):
    type: str
    text: str


class SynergyItem(BaseModel):
    type: str
    text: str


class RoutineAnalyzeResponse(BaseModel):
    rule_version: str = "foundation-1"
    evidence_status: str = "unverified_heuristic"
    conflicts: List[ConflictItem]
    synergies: List[SynergyItem]
    total_price_tier: str
    avg_match_score: int
    products: List[ProductSummary]


class FormulaLabRequest(BaseModel):
    ingredients_text: str
    persona_id: Optional[str] = "uap"


class ParsedIngredientDetail(BaseModel):
    name: str
    function: Optional[str] = ""
    comedogenic: Optional[int] = None
    irritancy: Optional[int] = None
    is_pore_clogging: bool = False
    is_fungal_trigger: bool = False
    fungal_trigger_note: Optional[str] = ""
    is_active: bool = False
    category_badge: str = "🔹 Formulation Base"
    safety_status: str = "unknown"
    benefits: List[str] = Field(default_factory=list)
    description: Optional[str] = ""


class SkinTypeCompatibility(BaseModel):
    score: int
    status: str
    verdict: str
    reason: str


class ConcernEfficacy(BaseModel):
    status: str
    score: int
    actives: List[str]
    mechanism: str


class FormulaLabResponse(BaseModel):
    score_kind: str = "unvalidated_heuristic"
    assessment_status: str = "unverified_formula"
    limitations: List[str] = Field(default_factory=lambda: ["Ingredient flags and fit scores are heuristics; concentrations, formulation performance and clinical safety are unverified."])
    predicted_match_score: int
    darmeto_points: float
    tier: Optional[str] = "Safe Everyday Base"
    status: str
    summary: Optional[str] = ""
    audit_log: List[str] = Field(default_factory=list)
    brighteners: List[str] = Field(default_factory=list)
    barrier: List[str] = Field(default_factory=list)
    smoothers: List[str] = Field(default_factory=list)
    irritants: List[str] = Field(default_factory=list)
    cloggers: List[str] = Field(default_factory=list)
    fungal_triggers: List[str] = Field(default_factory=list)
    is_fungal_safe: Optional[bool] = None
    is_fragrance_free: Optional[bool] = None
    is_alcohol_free: Optional[bool] = None
    is_pore_clogger_free: Optional[bool] = None
    is_oil_free: Optional[bool] = None
    total_ingredients: int = 0
    active_count: int = 0
    active_ratio: float = 0.0
    skin_compatibilities: Dict[str, SkinTypeCompatibility] = Field(default_factory=dict)
    concern_efficacies: Dict[str, ConcernEfficacy] = Field(default_factory=dict)
    ingredients_breakdown: List[ParsedIngredientDetail] = Field(default_factory=list)
    persona_label: Optional[str] = "Default Persona"
