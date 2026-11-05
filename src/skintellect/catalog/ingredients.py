from pathlib import Path

from skintellect.catalog.store import get_catalog
from skintellect.database import database
from skintellect.formulation.ingredient_facts import classify_ingredients

"""
Ingredient Intelligence Service
===============================
Provides fast search, multi-domain filtering, clinical safety indices,
and cross-referencing for 1,490+ cosmetic ingredients and their formulation products.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

_CACHED_INGREDIENTS: Optional[List[Dict[str, Any]]] = None
_CACHED_INGREDIENT_MAP: Optional[Dict[int, Dict[str, Any]]] = None
_CACHED_FUNCTIONS: Optional[List[str]] = None
_CACHE_STAMP = None


def _load_ingredients_cache() -> Tuple[List[Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    """Loads all ingredients and pre-computes product formulation counts."""
    global _CACHED_INGREDIENTS, _CACHED_INGREDIENT_MAP, _CACHED_FUNCTIONS, _CACHE_STAMP
    stamp = get_catalog().stamp
    if _CACHED_INGREDIENTS is not None and _CACHED_INGREDIENT_MAP is not None and stamp == _CACHE_STAMP:
        return _CACHED_INGREDIENTS, _CACHED_INGREDIENT_MAP

    if not Path(get_catalog().path).exists():
        return [], {}

    with database(get_catalog().path) as conn:
        c = conn.cursor()

        # Pre-count product occurrences per ingredient
        product_counts = {}
        try:
            c.execute("SELECT ingredient_id, COUNT(product_id) FROM product_ingredients GROUP BY ingredient_id")
            for i_id, count in c.fetchall():
                product_counts[i_id] = count
        except Exception:
            pass

        c.execute("""
            SELECT id, skinsort_id, name, slug, function, description, 
                   comedogenic, irritancy, is_pore_clogging, fungal_trigger, 
                   benefits_json, domains_json, sources_json
            FROM ingredients
            ORDER BY name ASC
        """)

        ing_list = []
        ing_map = {}
        functions_set = set()

        for row in c.fetchall():
            (i_id, skinsort_id, name, slug, function, description,
             comedogenic, irritancy, is_pore_clogging, fungal_trigger,
             benefits_json, domains_json, sources_json) = row

            benefits = []
            if benefits_json:
                try:
                    benefits = json.loads(benefits_json)
                except Exception:
                    pass

            domains = ["skin"]
            if domains_json:
                try:
                    domains = json.loads(domains_json)
                except Exception:
                    pass

            sources = ["skintellect", "incidecoder"]
            if sources_json:
                try:
                    sources = json.loads(sources_json)
                except Exception:
                    pass

            n_lower = (name or "").lower()
            func_str = (function or "").strip()
            if func_str:
                # Parse individual function tokens separated by bullet or comma
                tokens = re.split(r'[•·,;]', func_str)
                for t in tokens:
                    clean_t = t.strip()
                    if clean_t and len(clean_t) > 2:
                        functions_set.add(clean_t)

            facts = classify_ingredients([name]).groups
            is_bright = bool(facts['brighteners'])
            is_barrier = bool(facts['barrier'])
            is_smooth = bool(facts['smoothers'])
            is_fa = bool(fungal_trigger) or bool(facts['fungal_triggers'])
            is_clog = bool(is_pore_clogging) or int(comedogenic or 0) >= 3 or bool(facts['cloggers'])
            is_irrit = int(irritancy or 0) >= 2 or bool(facts['irritants'])

            # Infer additional domains based on cosmetic function
            inferred_domains = list(domains)
            if any(h in func_str.lower() for h in ["surfactant", "cleansing", "conditioning", "antistatic"]):
                if "hair" not in inferred_domains: inferred_domains.append("hair")
                if "body" not in inferred_domains: inferred_domains.append("body")
            if any(h in func_str.lower() for h in ["colorant", "pigment", "opacifying", "uv filter", "film former"]):
                if "makeup" not in inferred_domains: inferred_domains.append("makeup")
            if "skin" not in inferred_domains:
                inferred_domains.append("skin")

            # Category badge
            if is_fa and is_clog:
                badge = "⚠️ Fungal Trigger & Clogger"
                safety_class = "trigger"
            elif is_fa:
                badge = "⚠️ Malassezia Trigger"
                safety_class = "trigger"
            elif is_clog:
                badge = "⚠️ Comedogenic"
                safety_class = "caution"
            elif is_irrit:
                badge = "⚠️ Sensitizer / Fragrance"
                safety_class = "caution"
            elif is_bright:
                badge = "🌟 Brightener Active"
                safety_class = "beneficial"
            elif is_barrier:
                badge = "🛡️ Barrier Lipid"
                safety_class = "beneficial"
            elif is_smooth:
                badge = "🌿 Texture Smoother"
                safety_class = "beneficial"
            elif "humectant" in func_str.lower():
                badge = "💧 Deep Humectant"
                safety_class = "beneficial"
            elif "emollient" in func_str.lower():
                badge = "🧴 Emollient"
                safety_class = "unflagged"
            elif "solvent" in func_str.lower():
                badge = "🧪 Solvent / Vehicle"
                safety_class = "unflagged"
            elif "surfactant" in func_str.lower():
                badge = "🧼 Cleansing Surfactant"
                safety_class = "unflagged"
            else:
                badge = "🔹 Formulation Base"
                safety_class = "unknown"

            ing_obj = {
                "id": i_id,
                "skinsort_id": skinsort_id,
                "name": name,
                "slug": slug or name.lower().replace(" ", "-"),
                "function": func_str or "Unknown",
                "description": description or "",
                "comedogenic": int(comedogenic) if comedogenic is not None else None,
                "irritancy": int(irritancy) if irritancy is not None else None,
                "is_pore_clogging": is_clog,
                "is_fungal_trigger": is_fa,
                "fungal_trigger_note": fungal_trigger or ("Malassezia food trigger" if is_fa else ""),
                "is_active": is_bright or is_barrier or is_smooth,
                "category_badge": badge,
                "safety_class": safety_class,
                "benefits": benefits,
                "domains": inferred_domains,
                "sources": sources,
                "product_count": product_counts.get(i_id, 0)
            }

            ing_list.append(ing_obj)
            ing_map[i_id] = ing_obj


    _CACHED_INGREDIENTS = ing_list
    _CACHED_INGREDIENT_MAP = ing_map
    _CACHED_FUNCTIONS = sorted(list(functions_set))
    _CACHE_STAMP = stamp
    return _CACHED_INGREDIENTS, _CACHED_INGREDIENT_MAP


def get_ingredients(
    search: str = "",
    function: str = "all",
    domain: str = "all",
    comedogenic_max: Optional[int] = None,
    fungal_safe_only: bool = False,
    active_only: bool = False,
    page: int = 1,
    limit: int = 30
) -> Dict[str, Any]:
    """Queries, filters, and paginates the ingredient registry."""
    all_ings, _ = _load_ingredients_cache()

    filtered = all_ings

    if search.strip():
        q = search.strip().lower()
        filtered = [
            i for i in filtered 
            if q in i["name"].lower() or q in i["function"].lower() or any(q in b.lower() for b in i["benefits"])
        ]

    if function and function.lower() != "all":
        f_lower = function.lower()
        filtered = [i for i in filtered if f_lower in i["function"].lower()]

    if domain and domain.lower() != "all":
        d_lower = domain.lower()
        filtered = [i for i in filtered if d_lower in i["domains"]]

    if comedogenic_max is not None and comedogenic_max >= 0:
        filtered = [i for i in filtered if i["comedogenic"] is not None and i["comedogenic"] <= comedogenic_max]

    if fungal_safe_only:
        filtered = []  # Absence of a heuristic trigger is not a verified safety assessment.

    if active_only:
        filtered = [i for i in filtered if i["is_active"]]

    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit
    paged = filtered[offset:offset + limit]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "ingredients": paged
    }


def get_ingredient_detail(identifier: Any) -> Optional[Dict[str, Any]]:
    """Retrieves full ingredient dossier including products that formulate with it."""
    _, ing_map = _load_ingredients_cache()

    ing = None
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        ing = ing_map.get(int(identifier))
    elif isinstance(identifier, str):
        q = identifier.lower().strip()
        all_ings, _ = _load_ingredients_cache()
        ing = next((i for i in all_ings if i["slug"] == q or i["name"].lower() == q), None)

    if not ing:
        return None

    # Fetch top products formulating with this ingredient
    products = []
    if Path(get_catalog().path).exists():
        try:
            with database(get_catalog().path) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT p.id, p.brand, p.name, p.category, p.price_tier, p.image_url, 
                           p.match_score, p.rating, p.review_count, pi.is_key_ingredient, pi.key_note
                    FROM product_ingredients pi
                    JOIN products p ON pi.product_id = p.id
                    JOIN record_quality q ON q.product_id = p.id
                    WHERE pi.ingredient_id = ? AND q.is_seed = 0
                    ORDER BY p.rating DESC, p.review_count DESC
                    LIMIT 24
                """, (ing["id"],))

                for r in c.fetchall():
                    products.append({
                        "id": r[0],
                        "brand": r[1],
                        "name": r[2],
                        "category": r[3],
                        "price_tier": r[4],
                        "image_url": r[5],
                        "match_score": r[6],
                        "rating": r[7],
                        "review_count": r[8],
                        "is_key_active": bool(r[9]),
                        "benefit_text": r[10] or ""
                    })
        except Exception as e:
            print(f"Error fetching products for ingredient {ing['id']}: {e}")

    result = dict(ing)
    result["formulating_products"] = products
    result["total_products_count"] = ing.get("product_count", len(products))

    # Configured registries do not establish that a document was retrieved.
    result["source_profiles"] = {
        name: {"source": name, "verified": False, "status": "configured_only",
               "notice": "No supporting retrieved passage is attached to this ingredient."}
        for name in ing.get("sources", [])
    }

    return result


def get_ingredient_functions() -> List[str]:
    """Returns sorted unique function categories for dropdown filters."""
    _load_ingredients_cache()
    return _CACHED_FUNCTIONS or [
        "Humectant", "Emollient", "Skin Conditioning", "Surfactant",
        "Solvent", "Smoothing", "Preservative", "Antioxidant", "UV Filter",
        "Emulsifying", "Buffering", "Viscosity Controlling"
    ]
