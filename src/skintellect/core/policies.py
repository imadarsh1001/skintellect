"""
Pure domain policies for persona matching, safety checks, and evidence boundaries.
Deterministic: code enforces constraints; models provide natural language explanations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

from skintellect.core.entities import ProductEntity, SkinPersonaEntity


@dataclass
class PersonaMatchResult:
    product_id: int
    match_percentage: int
    is_eligible: bool
    status: str  # 'eligible', 'ineligible', 'partial_unknown'
    contributing_reasons: List[str] = field(default_factory=list)
    flagged_concerns: List[str] = field(default_factory=list)
    unknown_factors: List[str] = field(default_factory=list)
    coverage_score: float = 1.0  # Fraction of ingredients with known safety profiles


# Canonical normalization & grouping
COMMON_FUNGAL_TRIGGERS: Set[str] = {
    "polysorbate 20", "polysorbate 40", "polysorbate 60", "polysorbate 80",
    "isopropyl isostearate", "isopropyl myristate", "isopropyl palmitate",
    "peg-10 isostearate", "triolein", "glyceryl oleate", "sorbitan trioleate",
    "coconut oil", "olive oil", "shea butter", "cocoa butter", "stearic acid",
    "palmitic acid", "myristic acid", "lauric acid", "oleic acid"
}

COMMON_DRYING_ALCOHOLS: Set[str] = {
    "alcohol denat", "alcohol denat.", "denatured alcohol", "ethanol",
    "isopropyl alcohol", "sd alcohol 40", "sd alcohol 40-b"
}

COMMON_FRAGRANCES: Set[str] = {
    "fragrance", "parfum", "perfume", "linalool", "limonene", "citronellol",
    "geraniol", "eugenol", "hydroxycitronellal", "cinnamal", "benzyl alcohol"
}


def normalize_ingredient_name(name: str) -> str:
    """Standardizes ingredient string for deterministic comparison."""
    cleaned = name.lower().strip()
    for char in ["*", "^", "†", "‡", '"']:
        cleaned = cleaned.replace(char, "")
    return " ".join(cleaned.split())


def evaluate_persona_match(
    product: ProductEntity,
    persona: SkinPersonaEntity
) -> PersonaMatchResult:
    """
    Evaluates how well a product formulation aligns with a buyer's skin persona.
    Separates user fit from store popularity and evidence coverage.
    """
    if not product.ingredients or product.formula_status == "missing":
        return PersonaMatchResult(
            product_id=product.id,
            match_percentage=50,
            is_eligible=True,
            status="partial_unknown",
            unknown_factors=["Formula list is unrecorded or incomplete in catalog"],
            coverage_score=0.0
        )

    norm_ings = {normalize_ingredient_name(i) for i in product.ingredients}
    reasons: List[str] = []
    concerns: List[str] = []
    unknowns: List[str] = []
    score = 100

    # 1. Fungal Acne Exclusion
    if persona.exclusions.fungal_acne_safe:
        triggers_found = norm_ings.intersection(COMMON_FUNGAL_TRIGGERS)
        if triggers_found:
            concerns.append(f"Contains {len(triggers_found)} fungal acne trigger(s): {', '.join(sorted(triggers_found)[:3])}")
            score -= 30

    # 2. Fragrance-Free Exclusion
    if persona.exclusions.fragrance_free:
        fragrances_found = norm_ings.intersection(COMMON_FRAGRANCES)
        if fragrances_found:
            concerns.append(f"Contains fragrance or fragrance allergens: {', '.join(sorted(fragrances_found)[:3])}")
            score -= 25

    # 3. Alcohol-Free Exclusion
    if persona.exclusions.alcohol_free:
        alcohols_found = norm_ings.intersection(COMMON_DRYING_ALCOHOLS)
        if alcohols_found:
            concerns.append(f"Contains drying alcohol: {', '.join(sorted(alcohols_found)[:2])}")
            score -= 20

    # 4. Custom Exclusions
    for custom in persona.exclusions.custom_excluded_ingredients:
        norm_custom = normalize_ingredient_name(custom)
        if any(norm_custom in ing for ing in norm_ings):
            concerns.append(f"Contains excluded ingredient: {custom}")
            score -= 40

    # 5. Skin Type Compatibility
    if persona.skin_type == "dry":
        if any(i in norm_ings for i in ["ceramide", "ceramide np", "glycerin", "hyaluronic acid", "squalane", "petrolatum", "panthenol"]):
            reasons.append("Rich in barrier-supportive lipids and humectants for dry skin")
            score = min(100, score + 10)
    elif persona.skin_type == "oily":
        if any(i in norm_ings for i in ["niacinamide", "zinc pca", "salicylic acid", "green tea", "centella asiatica"]):
            reasons.append("Contains sebum-balancing or soothing lightweight actives suitable for oily skin")
            score = min(100, score + 10)

    # 6. Sensitivity
    if persona.sensitivity in ("slightly_sensitive", "very_sensitive"):
        if any(i in norm_ings for i in ["centella asiatica", "allantoin", "bisabolol", "madecassoside", "oat", "colloidal oatmeal"]):
            reasons.append("Contains proven calming and anti-inflammatory botanicals")
            score = min(100, score + 5)

    final_score = max(0, min(100, score))
    is_eligible = len(concerns) == 0 or final_score >= 60
    status = "eligible" if is_eligible else "ineligible"

    return PersonaMatchResult(
        product_id=product.id,
        match_percentage=final_score,
        is_eligible=is_eligible,
        status=status,
        contributing_reasons=reasons,
        flagged_concerns=concerns,
        unknown_factors=unknowns,
        coverage_score=1.0
    )
