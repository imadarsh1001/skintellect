"""
Formulation API router: Product dupes and alternative formulation inspection.
"""

from fastapi import APIRouter
from skintellect.research.alternatives import get_dupes_for_product

router = APIRouter(tags=["Formulation"])


@router.get("/api/dupes/{product_id}")
def find_dupes(product_id: int):
    """Finds algorithmic budget dupes and formula twins."""
    dupes = get_dupes_for_product(product_id)
    return {"product_id": product_id, "dupes": dupes}
