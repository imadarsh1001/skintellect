from skintellect.catalog.store import get_catalog

"""
Catalog Service - SQLite Queries, Filtering, Sorting, and Dynamic Scoring
"""


from typing import Any, Dict, List, Optional
from skintellect.formulation.scoring import score_product_for_persona

from skintellect.catalog.personas import get_all_personas


def _load_catalog_cache():
    return get_catalog().display_records()


# score_product_for_persona is canonically defined and imported from skintellect.formulation.scoring



def get_products(
    page: int = 1,
    limit: int = 36,
    category: str = "all",
    domain: str = "all",
    price_tier: str = "all",
    country: str = "all",
    goal: str = "all",
    min_match: int = 0,
    search: str = "",
    fungal_safe: bool = False,
    fragrance_free: bool = False,
    oil_free: bool = False,
    pore_free: bool = False,
    sort_by: str = "composite_desc",
    persona_id: str = "uap",
    include_seeds: bool = False
) -> Dict[str, Any]:
    """Returns filtered, sorted, paginated products scored dynamically for persona."""
    catalog = _load_catalog_cache()
    personas = get_all_personas()
    active_persona = next((p for p in personas if p["id"] == persona_id or p["username"] == persona_id), personas[0])

    scored_list = []
    search_lower = search.strip().lower()

    for item in catalog:
        if item.get("is_seed") and not include_seeds:
            continue
        # Domain filter (skin, hair, body, makeup)
        if domain != "all":
            item_domain = (item.get("domain") or "skin").lower()
            if domain.lower() != item_domain:
                continue

        # Fast pre-filtering
        if category != "all":
            target_cat = category.strip().lower()
            cat_disp = (item.get("category_display") or "").lower()
            cat_raw = (item.get("category") or "").lower()
            if target_cat not in cat_disp and target_cat not in cat_raw:
                continue

        if country != "all" and (item.get("brand_country") or "").lower() != country.lower():
            continue
        if price_tier != "all" and (item.get("price_tier") or "$$") != price_tier:
            continue
        if goal != "all":
            goals = [str(g).lower() for g in item.get("parsed_skin_goals", [])]
            if not any(goal.lower() in g for g in goals):
                continue
        if fungal_safe and item.get("fungal_acne_safe") != 1:
            continue
        if fragrance_free and item.get("fragrance_free") != 1:
            continue
        if oil_free and item.get("oil_free") != 1:
            continue
        if pore_free and item.get("pore_clogger_free") != 1:
            continue

        if search_lower:
            haystack = f"{item.get('name', '')} {item.get('brand', '')} {item.get('category_display', '')} {item.get('category', '')} {item.get('brand_country', '')} {item.get('short_desc', '')}".lower()
            actives_str = " ".join(item.get("analysis", {}).get("brighteners", []) + item.get("analysis", {}).get("hydrators", []) + item.get("analysis", {}).get("smoothers", [])).lower()
            if search_lower not in haystack and search_lower not in actives_str:
                continue

        # Dynamic Scoring
        match_score, composite_score, reasons = score_product_for_persona(item, active_persona)
        if match_score < min_match:
            continue

        # Shallow copy with updated scores
        p_copy = dict(item)
        p_copy["match_score"] = match_score
        p_copy["composite_score"] = composite_score
        p_copy["match_reasons"] = reasons

        excl = active_persona.get('safety_exclusions', {})
        flagged = []
        if excl.get('fungal_acne_safe') and item.get('fungal_acne_safe', 0) == 0:
            flagged.append('Fungal Acne Trigger')
        if excl.get('fragrance_free') and item.get('fragrance_free', 0) == 0:
            flagged.append('Fragrance / Allergen')
        if excl.get('alcohol_free') and item.get('alcohol_free', 0) == 0:
            flagged.append('Drying Alcohol')

        match_status = 'contraindicated' if flagged else ('unknown' if not item.get('names') else 'match')
        p_copy['persona_match'] = {
            'is_match': len(flagged) == 0 and match_score >= 60,
            'match_status': match_status,
            'score': match_score,
            'contraindications_found': flagged,
            'matched_goals': [g for g in item.get('parsed_skin_goals', []) if g in active_persona.get('target_concerns', [])],
            'explanation': '; '.join(reasons) if reasons else f"{match_score}% compatible with {active_persona.get('label', 'selected profile')}"
        }
        scored_list.append(p_copy)

    # Sorting
    if sort_by == "composite_desc":
        scored_list.sort(key=lambda x: (x["composite_score"], x["match_score"], x.get("rating", 0.0)), reverse=True)
    elif sort_by == "match_desc":
        scored_list.sort(key=lambda x: (x["match_score"], x["composite_score"], x.get("rating", 0.0)), reverse=True)
    elif sort_by == "price_asc":
        tier_map = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        scored_list.sort(key=lambda x: tier_map.get(x.get("price_tier", "$$"), 2))
    elif sort_by == "price_desc":
        tier_map = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        scored_list.sort(key=lambda x: tier_map.get(x.get("price_tier", "$$"), 2), reverse=True)
    elif sort_by == "rating_desc":
        scored_list.sort(key=lambda x: (x.get("rating", 0.0), x.get("review_count", 0)), reverse=True)
    elif sort_by == "reviews_desc":
        scored_list.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    elif sort_by == "name_asc":
        scored_list.sort(key=lambda x: x.get("name", "").lower())
    elif sort_by == "brand_asc":
        scored_list.sort(key=lambda x: x.get("brand", "").lower())

    total = len(scored_list)
    total_pages = max(1, (total + limit - 1) // limit)
    start = (page - 1) * limit
    end = start + limit
    paged_items = scored_list[start:end]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": paged_items,
        "active_persona": active_persona
    }


def get_product_by_id(product_id: int, persona_id: str = "uap", records=None) -> Optional[Dict[str, Any]]:
    """Returns deep product details including ingredients, reviews, and similar dupes."""
    catalog = records if records is not None else _load_catalog_cache()
    p = next((x for x in catalog if x["id"] == product_id), None)
    if not p:
        return None

    personas = get_all_personas()
    active_persona = next((x for x in personas if x["id"] == persona_id or x["username"] == persona_id), personas[0])

    p_copy = dict(p)
    match_score, composite_score, reasons = score_product_for_persona(p, active_persona)
    p_copy["match_score"] = match_score
    p_copy["composite_score"] = composite_score
    p_copy["match_reasons"] = reasons

    excl = active_persona.get('safety_exclusions', {})
    flagged = []
    if excl.get('fungal_acne_safe') and p.get('fungal_acne_safe', 0) == 0:
        flagged.append('Fungal Acne Trigger')
    if excl.get('fragrance_free') and p.get('fragrance_free', 0) == 0:
        flagged.append('Fragrance / Allergen')
    if excl.get('alcohol_free') and p.get('alcohol_free', 0) == 0:
        flagged.append('Drying Alcohol')

    match_status = 'contraindicated' if flagged else ('unknown' if not p.get('names') else 'match')
    p_copy['persona_match'] = {
        'is_match': len(flagged) == 0 and match_score >= 60,
        'match_status': match_status,
        'score': match_score,
        'contraindications_found': flagged,
        'matched_goals': [g for g in p.get('parsed_skin_goals', []) if g in active_persona.get('target_concerns', [])],
        'explanation': '; '.join(reasons) if reasons else f"{match_score}% compatible with {active_persona.get('label', 'selected profile')}"
    }
    try:
        from skintellect.research.alternatives import get_dupes_for_product
        dupes = get_dupes_for_product(product_id)
        p_copy["alternatives"] = dupes
        if not p_copy.get("similar_products"):
            p_copy["similar_products"] = dupes
    except Exception:
        p_copy["alternatives"] = []

    return p_copy


def get_catalog_stats() -> Dict[str, Any]:
    """Computes global catalog metrics for category, country, and price distributions."""
    catalog = _load_catalog_cache()
    cat_counts: Dict[str, int] = {}
    country_counts: Dict[str, int] = {}
    tier_counts: Dict[str, int] = {"$": 0, "$$": 0, "$$$": 0, "$$$$": 0}
    total_reviews = 0
    enriched = 0

    for p in catalog:
        c = p.get("category_display", "Moisturizers")
        cat_counts[c] = cat_counts.get(c, 0) + 1

        co = p.get("brand_country", "International")
        country_counts[co] = country_counts.get(co, 0) + 1

        tier = p.get("price_tier", "$$")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        total_reviews += len(p.get("reviews", []))
        if p.get("has_detail") == 1:
            enriched += 1

    return {
        "total_products": len(catalog),
        "enriched_products": enriched,
        "total_reviews": total_reviews,
        "total_ingredients": 1490,
        "category_counts": cat_counts,
        "country_counts": country_counts,
        "price_tier_counts": tier_counts
    }



def load_records(db_path=None):
    return get_catalog(db_path).records()
