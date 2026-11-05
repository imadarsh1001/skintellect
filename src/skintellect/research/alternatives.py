"""Weighted recorded-ingredient similarity and legacy response adaptation."""


import math
from collections import Counter

from skintellect.catalog.products import load_records
from skintellect.research.models import SearchIntent
from skintellect.research.search import brief, eligibility


def alternatives(product_id, intent, records=None, product_ids=None):
    records = load_records() if records is None else records
    target = next((p for p in records if p['id'] == product_id), None)
    if not target:
        return None
    if intent.unresolved_terms:
        return {'product_id': product_id, 'alternatives': [], 'needs_clarification': intent.unresolved_terms}
    frequencies = Counter(n for p in records if p.get('is_seed') == 0 for n in set(p['names']))
    count = sum(p.get('is_seed') == 0 for p in records)
    weights = {n: math.log((count + 1)/(f + 1)) + 1 for n, f in frequencies.items()}
    a = set(target['names'])
    candidates = []
    for p in records:
        if product_ids is not None and p['id'] not in product_ids:
            continue
        if p['id'] == product_id or p.get('is_seed') != 0 or p.get('category') != target.get('category') or p.get('domain') != target.get('domain'):
            continue
        if intent.domain != 'all' and p.get('domain') != intent.domain:
            continue
        if intent.category != 'all' and intent.category.casefold().rstrip('s') not in (p.get('category') or '').casefold():
            continue
        checks = eligibility(p, intent)
        if any(c['status'] != 'pass' for c in checks):
            continue
        b = set(p['names'])
        union, shared = a | b, a & b
        if not shared:
            continue
        score = sum(weights.get(n, 1) for n in shared)/sum(weights.get(n, 1) for n in union)
        candidates.append(brief(p) | {'weighted_similarity': round(score, 4),
            'jaccard_baseline': round(len(shared)/len(union), 4), 'shared_ingredients': sorted(shared),
            'removed_ingredients': sorted(a-b), 'added_ingredients': sorted(b-a), 'checks': checks,
            'price_preference': int(p.get('price_tier') in intent.preferred_price_tiers)})
    candidates.sort(key=lambda x: (-x['weighted_similarity'], -x['price_preference'], x['id']))
    return {'product_id': product_id, 'alternatives': candidates[:intent.limit], 'target': brief(target),
            'notice': 'Recorded ingredient similarity does not establish matching concentrations, performance, or safety.'}

def get_dupes_for_product(product_id):
    result = alternatives(product_id, SearchIntent(domain="all"))
    if not result:
        return []
    return [p | {"similarity": round(p["weighted_similarity"] * 100),
                 "shared_actives": p["shared_ingredients"][:4],
                 "similarity_kind": "weighted_ingredient_overlap",
                 "limitations": result["notice"]} for p in result["alternatives"]]
