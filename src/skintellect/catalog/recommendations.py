from skintellect.formulation.ingredient_facts import classify_ingredients
from skintellect.formulation.scoring import calculate_darmeto_points

"""
Skintellect & Filter Engine
====================================
Analyzes crawled products and evaluates formulations specifically tailored for:
- Skin Type: Combination (Oily T-zone, Dry/Normal cheeks)
- Sensitivity: Slightly Sensitive (Occasionally reactive)
- Target Concerns: Dark Spots, Dryness & Dehydration, Dullness, Texture
"""

import json
import os
import re
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
from skintellect.config import DB_PATH

BASE_DIR = os.path.dirname(DB_PATH)

# Dermatological Pattern Rules





def resolve_routine_and_size(p: Dict[str, Any]) -> Tuple[str, str]:
    """Resolves accurate skincare routine step and net volume based on product category & naming."""
    name_l = (p.get('name') or '').lower()
    cat_slug = (p.get('category_slug') or '').lower()
    cat_name = (p.get('category') or '').lower()

    if any(k in name_l for k in ['cleanser', 'cleansing', 'wash', 'foam']) or 'cleanser' in cat_slug or 'cleanser' in cat_name:
        step = "Step 1: Cleanse (AM/PM)"
        def_size = "150 ml / 5.1 fl oz"
    elif any(k in name_l for k in ['toner', 'essence', 'mist', 'pad']) or 'toner' in cat_slug or 'toner' in cat_name:
        step = "Step 2: Tone & Prep (AM/PM)"
        def_size = "150 ml / 5.1 fl oz"
    elif any(k in name_l for k in ['serum', 'ampoule', 'drop', 'booster']) or 'serum' in cat_slug or 'serum' in cat_name:
        step = "Step 3: Treat & Target (AM/PM)"
        def_size = "30 ml / 1.0 fl oz"
    elif any(k in name_l for k in ['sun', 'spf', 'uv', 'fluid']) or 'sunscreen' in cat_slug or 'sunscreen' in cat_name:
        step = "Step 5: Protect (AM Daily)"
        def_size = "50 ml / 1.7 fl oz"
    elif 'eye' in name_l or 'eye' in cat_slug:
        step = "Targeted: Eye Area (AM/PM)"
        def_size = "15 ml / 0.5 fl oz"
    elif 'mask' in name_l or 'peel' in name_l or 'mask' in cat_slug:
        step = "Weekly Treatment: Nourish (1-2x/week)"
        def_size = "75 ml / 2.5 fl oz"
    else:
        step = "Step 4: Moisturize & Barrier (AM/PM)"
        def_size = "50 ml / 1.7 fl oz"

    raw_size = p.get('size')
    m = re.search(r'\b(\d+(?:\.\d+)?\s*(?:ml|fl\.?\s*oz|g|oz))\b', f"{p.get('name', '')} {p.get('short_desc') or ''}", re.IGNORECASE)
    size = m.group(1).strip() if m else (raw_size if (raw_size and raw_size != '50 ml / 1.7 fl oz') else def_size)

    return step, size


def analyze_product_ingredients(ingredients_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    return classify_ingredients(ingredients_list, profile='recommendation').groups


def get_recommendations(
    category: Optional[str] = None,
    country: Optional[str] = None,
    skin_goal: Optional[str] = None,
    min_match_score: int = 85,
    must_be_fragrance_free: bool = True,
    must_be_alcohol_free: bool = True,
    must_be_fungal_safe: bool = False,
    must_be_oil_free: bool = False,
    must_be_silicone_free: bool = False,
    max_pore_cloggers: int = 1,
    price_tier: Optional[str] = None,
    max_price_tier: Optional[int] = None,
    search_query: Optional[str] = None,
    db_path: str = DB_PATH
) -> List[Dict[str, Any]]:
    """
    Scores and ranks products based on Skintellect's personalized match score
    and dermatological benefits addressing dark spots, dryness, dullness, and texture.
    Supports filtering by category, brand country, skin goal, price tier, and formulation safety.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM products WHERE match_score >= ?"
    params: List[Any] = [min_match_score]

    if category and category.lower() != 'all':
        cat_clean = category.lower().replace(" ", "-")
        query += " AND (LOWER(category_slug) = ? OR LOWER(category) LIKE ?)"
        params.extend([cat_clean, f"%{category.lower()}%"])

    if country and country.lower() != 'all':
        query += " AND LOWER(brand_country) = ?"
        params.append(country.lower())

    if price_tier and price_tier.lower() != 'all':
        query += " AND price_tier = ?"
        params.append(price_tier)

    if max_price_tier is not None:
        query += " AND price_tier_num <= ?"
        params.append(max_price_tier)

    if must_be_fungal_safe:
        query += " AND fungal_acne_safe = 1"
    if must_be_oil_free:
        query += " AND oil_free = 1"
    if must_be_silicone_free:
        query += " AND silicone_free = 1"

    query += " ORDER BY match_score DESC, rating DESC"
    cur.execute(query, params)
    products = [dict(r) for r in cur.fetchall()]
    conn.close()

    results = []
    for p in products:
        ings = []
        if p['ingredients_json']:
            try:
                ings = json.loads(p['ingredients_json'])
            except Exception:
                pass

        # Parse skin goals
        goals = []
        if p['skin_goals']:
            try:
                goals = json.loads(p['skin_goals'])
            except Exception:
                pass
        p['parsed_skin_goals'] = goals

        # Parse badges
        badges = []
        if p['badges']:
            try:
                badges = json.loads(p['badges'])
            except Exception:
                pass
        p['parsed_badges'] = badges

        # Filter by skin goal if requested
        if skin_goal and skin_goal.lower() != 'all':
            if not any(skin_goal.lower() in g.lower() for g in goals):
                continue
        
        analysis = analyze_product_ingredients(ings)

        # Apply strict safety gates for sensitive/combination skin
        if must_be_fragrance_free and p['fragrance_free'] == 0:
            continue
        if must_be_alcohol_free and p['alcohol_free'] == 0:
            continue
        if len(analysis['pore_cloggers']) > max_pore_cloggers:
            continue
        if len(analysis['irritants']) > 0 and must_be_fragrance_free:
            continue

        # Search query filter across name, brand, and ingredients
        if search_query:
            sq = search_query.lower()
            text = (f"{p['name']} {p['brand']} {p['category']} {p['brand_country']} " +
                    " ".join(analysis['brighteners'] + analysis['hydrators'] + analysis['smoothers'])).lower()
            if sq not in text:
                continue

        # Calculate clinical Darmeto fit points and composite score via canonical scoring engine
        darmeto_res = calculate_darmeto_points(
            match_score=p['match_score'] or 85,
            analysis={
                'brighteners': analysis['brighteners'],
                'barrier': analysis['hydrators'],
                'smoothers': analysis['smoothers'],
                'cloggers': analysis['pore_cloggers'],
                'irritants': analysis['irritants'],
            },
            fungal_acne_safe=(p['fungal_acne_safe'] == 1),
            pore_clogger_free=(p['pore_clogger_free'] == 1),
            oil_free=(p['oil_free'] == 1),
            rating=p.get('rating'),
        )

        p['composite_score'] = darmeto_res['darmeto_points']
        p['darmeto_points'] = darmeto_res['darmeto_points']
        p['darmeto_tier'] = darmeto_res['tier']
        p['analysis'] = analysis
        p['ingredients_count'] = len(ings)
        p['routine_step'], p['size'] = resolve_routine_and_size(p)
        p_tier = p.get('price_tier') or '$$'
        p['price_tier'] = p_tier
        p['price_tier_num'] = p.get('price_tier_num') or len(p_tier)
        tier_ranges = {
            '$': 'Budget (<$15)',
            '$$': 'Moderate ($15-$30)',
            '$$$': 'Premium ($30-$60)',
            '$$$$': 'Luxury ($60+)'
        }
        p['price_range'] = tier_ranges.get(p_tier, p.get('price_range') or 'Moderate ($15-$30)')
        
        # Parse community sentiment & key actives
        survey = []
        if p.get('community_survey'):
            try: survey = json.loads(p['community_survey'])
            except Exception: pass
        p['community_survey'] = survey

        breakdown = {}
        if p.get('rating_breakdown'):
            try: breakdown = json.loads(p['rating_breakdown'])
            except Exception: pass
        p['rating_breakdown'] = breakdown

        key_actives = []
        if p.get('key_actives_json'):
            try: key_actives = json.loads(p['key_actives_json'])
            except Exception: pass
        p['key_actives'] = key_actives

        results.append(p)

    results.sort(key=lambda x: x['composite_score'], reverse=True)
    return results


def search_products(
    category: Optional[str] = None,
    country: Optional[str] = None,
    skin_goal: Optional[str] = None,
    min_match: int = 85,
    fragrance_free: bool = False,
    fungal_safe: bool = False,
    oil_free: bool = False,
    silicone_free: bool = False,
    alcohol_free: bool = False,
    min_rating: float = 0.0,
    price_tier: Optional[str] = None,
    max_price_tier: Optional[int] = None,
    active_term: Optional[str] = None,
    search_query: Optional[str] = None,
    max_pore_cloggers: Optional[int] = 1,
    limit: int = 20,
    db_path: str = DB_PATH
) -> List[Dict[str, Any]]:
    """Filters products across customizable criteria from the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM products WHERE match_score >= ?"
    params: List[Any] = [min_match]

    if category and category.lower() != 'all':
        cat_clean = category.lower().replace(" ", "-")
        query += " AND (LOWER(category_slug) = ? OR LOWER(category) LIKE ?)"
        params.extend([cat_clean, f"%{category.lower()}%"])

    if country and country.lower() != 'all':
        query += " AND LOWER(brand_country) = ?"
        params.append(country.lower())

    if price_tier and price_tier.lower() != 'all':
        query += " AND price_tier = ?"
        params.append(price_tier)

    if max_price_tier is not None:
        query += " AND price_tier_num <= ?"
        params.append(max_price_tier)

    if fragrance_free:
        query += " AND fragrance_free = 1"
    if fungal_safe:
        query += " AND fungal_acne_safe = 1"
    if oil_free:
        query += " AND oil_free = 1"
    if silicone_free:
        query += " AND silicone_free = 1"
    if alcohol_free:
        query += " AND alcohol_free = 1"
    if min_rating > 0:
        query += " AND rating >= ?"
        params.append(min_rating)

    query += " ORDER BY match_score DESC, rating DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    filtered = []
    for r in rows:
        ings = []
        if r['ingredients_json']:
            try:
                ings = json.loads(r['ingredients_json'])
            except Exception:
                pass
        analysis = analyze_product_ingredients(ings)

        # Parse skin goals
        goals = []
        if r['skin_goals']:
            try:
                goals = json.loads(r['skin_goals'])
            except Exception:
                pass
        r['parsed_skin_goals'] = goals

        # Parse badges
        badges = []
        if r['badges']:
            try:
                badges = json.loads(r['badges'])
            except Exception:
                pass
        r['parsed_badges'] = badges

        if skin_goal and skin_goal.lower() != 'all':
            if not any(skin_goal.lower() in g.lower() for g in goals):
                continue

        if max_pore_cloggers is not None and len(analysis['pore_cloggers']) > max_pore_cloggers:
            continue

        if active_term:
            term_lower = active_term.lower()
            all_text = (r['name'] + " " + r['brand'] + " " + str(r['ingredients_json'])).lower()
            if term_lower not in all_text:
                continue

        if search_query:
            sq = search_query.lower()
            all_text = (f"{r['name']} {r['brand']} {r['category']} {r['brand_country']} " +
                        str(r['ingredients_json'])).lower()
            if sq not in all_text:
                continue

        r['analysis'] = analysis
        filtered.append(r)

    return filtered[:limit]


def get_all_products_catalog(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Returns the complete product catalog enriched with dermatological ingredient analysis,
    composite scoring, parsed JSON objects, and normalized taxonomy for interactive UI rendering.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY match_score DESC, rating DESC")
    rows = [dict(r) for r in cur.fetchall()]

    # Fetch reviews for all products
    reviews_by_pid = {}
    try:
        cur.execute("SELECT skinsort_post_id, product_id, author, reviewer_skin_type, rating, date_posted, formulation_version, review_text, tags_json FROM reviews ORDER BY id ASC")
        for rr in cur.fetchall():
            rd = dict(rr)
            if rd.get('tags_json'):
                try: rd['tags'] = json.loads(rd['tags_json'])
                except Exception: rd['tags'] = []
            else:
                rd['tags'] = []
            reviews_by_pid.setdefault(rd['product_id'], []).append(rd)
    except Exception:
        pass
    conn.close()

    catalog = []
    for r in rows:
        r['reviews'] = reviews_by_pid.get(r['id'], [])
        ings = []
        if r['ingredients_json']:
            try:
                ings = json.loads(r['ingredients_json'])
            except Exception:
                pass

        goals = []
        if r['skin_goals']:
            try:
                goals = json.loads(r['skin_goals'])
            except Exception:
                pass
        r['parsed_skin_goals'] = goals

        badges = []
        if r['badges']:
            try:
                badges = json.loads(r['badges'])
            except Exception:
                pass
        r['parsed_badges'] = badges

        analysis = analyze_product_ingredients(ings)
        r['analysis'] = analysis
        r['ingredients_count'] = len(ings)

        # Calculate composite dermatological fit score
        score = r['match_score'] or 85
        score += min(len(analysis['brighteners']) * 3, 9)
        score += min(len(analysis['hydrators']) * 2, 8)
        score += min(len(analysis['smoothers']) * 2, 6)
        if r['fungal_acne_safe'] == 1: score += 4
        if r['pore_clogger_free'] == 1: score += 3
        if r['oil_free'] == 1: score += 2
        score -= len(analysis['pore_cloggers']) * 4
        score -= len(analysis['irritants']) * 6
        if r['rating'] and r['rating'] >= 4.0: score += 3

        r['composite_score'] = round(score, 1)

        r['parsed_ingredients'] = ings
        r['ing_set'] = {i['name'].strip().lower() for i in ings if isinstance(i, dict) and i.get('name')}
        p_tier = r.get('price_tier') or '$$'
        r['price_tier'] = p_tier
        r['price_tier_num'] = r.get('price_tier_num') or len(p_tier)
        tier_ranges = {
            '$': 'Budget (<$15)',
            '$$': 'Moderate ($15-$30)',
            '$$$': 'Premium ($30-$60)',
            '$$$$': 'Luxury ($60+)'
        }
        r['price_range'] = tier_ranges.get(p_tier, r.get('price_range') or 'Moderate ($15-$30)')
        calc_step, calc_size = resolve_routine_and_size(r)
        r['routine_step'] = calc_step
        r['size'] = calc_size
        r['darmeto_points'] = r['composite_score']

        # Parse community sentiment, rating breakdown & key actives
        survey = []
        if r.get('community_survey'):
            try:
                survey = json.loads(r['community_survey'])
            except Exception:
                pass
        r['community_survey'] = survey

        breakdown = {}
        if r.get('rating_breakdown'):
            try:
                breakdown = json.loads(r['rating_breakdown'])
            except Exception:
                pass
        r['rating_breakdown'] = breakdown

        key_actives = []
        if r.get('key_actives_json'):
            try:
                key_actives = json.loads(r['key_actives_json'])
            except Exception:
                pass
        r['key_actives'] = key_actives

        key_benefits = []
        if r.get('key_benefits_summary'):
            try:
                key_benefits = json.loads(r['key_benefits_summary'])
            except Exception:
                pass
        r['key_benefits'] = key_benefits

        # Standardize category display
        cat_slug = r.get('category_slug') or 'moisturizers'
        cat_map = {
            'moisturizers': 'Moisturizers',
            'sunscreens': 'Sunscreens',
            'serums': 'Serums',
            'toners': 'Toners',
            'face-cleansers': 'Cleansers',
            'cleansers': 'Cleansers',
            'eye-care': 'Eye Care',
            'treatments': 'Treatments',
            'exfoliators': 'Exfoliators',
            'face-masks': 'Face Masks',
            'lip-balms': 'Lip Balms'
        }
        r['category_display'] = cat_map.get(cat_slug, (r.get('category') or 'Moisturizers').capitalize())
        r['brand_country'] = r.get('brand_country') or 'International'
        catalog.append(r)

    # Pre-compute top formula dupes & alternatives for every product
    ing_sets = {p['id']: p.pop('ing_set', set()) for p in catalog}

    for p in catalog:
        p_set = ing_sets.get(p['id'], set())
        cat = p.get('category_slug')
        candidates = []
        for q in catalog:
            if q['id'] == p['id']:
                continue
            if cat and q.get('category_slug') != cat:
                continue
            q_set = ing_sets.get(q['id'], set())
            if len(p_set) >= 3 and len(q_set) >= 3:
                inter = p_set & q_set
                union = p_set | q_set
                sim = round(len(inter) / len(union) * 100)
                if sim >= 15:
                    candidates.append({
                        "id": q['id'],
                        "brand": q['brand'],
                        "name": q['name'],
                        "similarity": sim,
                        "price_tier": q.get('price_tier', '$$'),
                        "price_range": q.get('price_range', 'Moderate ($15-$30)'),
                        "match_score": q.get('match_score') or 85,
                        "rating": q.get('rating'),
                        "review_count": q.get('review_count'),
                        "shared_count": len(inter),
                        "shared_actives": [x.title() for x in list(inter)[:4]],
                        "fungal_acne_safe": q.get('fungal_acne_safe', 0),
                        "fragrance_free": q.get('fragrance_free', 0),
                        "is_cheaper": (q.get('price_tier_num', 2) < p.get('price_tier_num', 2))
                    })
            elif len(p_set) < 3:
                candidates.append({
                    "id": q['id'],
                    "brand": q['brand'],
                    "name": q['name'],
                    "similarity": min(95, max(70, round(((p.get('match_score') or 85) + (q.get('match_score') or 85)) / 2))),
                    "price_tier": q.get('price_tier', '$$'),
                    "price_range": q.get('price_range', 'Moderate ($15-$30)'),
                    "match_score": q.get('match_score') or 85,
                    "rating": q.get('rating'),
                    "review_count": q.get('review_count'),
                    "shared_count": 0,
                    "shared_actives": (q.get('analysis', {}).get('brighteners', [])[:2] + q.get('analysis', {}).get('hydrators', [])[:2]),
                    "fungal_acne_safe": q.get('fungal_acne_safe', 0),
                    "fragrance_free": q.get('fragrance_free', 0),
                    "is_cheaper": (q.get('price_tier_num', 2) < p.get('price_tier_num', 2))
                })
        candidates.sort(key=lambda x: (x['similarity'], x['match_score'] or 0), reverse=True)
        p['similar_products'] = candidates[:4]

    catalog.sort(key=lambda x: x['composite_score'], reverse=True)
    return catalog


if __name__ == "__main__":
    recs = get_recommendations(min_match_score=90)
    print(f"\nTop Recommendations Found: {len(recs)}")
    for idx, r in enumerate(recs[:5], 1):
        print(f"#{idx} [{r['composite_score']} pts | {r['match_score']}% Match] {r['brand']} - {r['name']}")
