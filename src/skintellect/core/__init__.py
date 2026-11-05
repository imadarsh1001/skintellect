"""
Core domain layer: Entities, policies, and contracts.
"""

from skintellect.core.entities import (
    AspectObservationEntity,
    IngredientEntity,
    PersonaExclusionsEntity,
    ProductEntity,
    ReviewEntity,
    ScientificReferenceEntity,
    SkinPersonaEntity,
)
from skintellect.core.policies import (
    PersonaMatchResult,
    evaluate_persona_match,
    normalize_ingredient_name,
)

__all__ = [
    "ProductEntity",
    "IngredientEntity",
    "SkinPersonaEntity",
    "PersonaExclusionsEntity",
    "ReviewEntity",
    "AspectObservationEntity",
    "ScientificReferenceEntity",
    "PersonaMatchResult",
    "evaluate_persona_match",
    "normalize_ingredient_name",
]
