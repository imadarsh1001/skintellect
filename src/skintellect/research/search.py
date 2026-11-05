from skintellect.catalog.store import get_catalog

"""Interpret queries and enforce deterministic ingredient eligibility."""




import re

from skintellect.catalog.products import load_records
from skintellect.research.evidence import check_ingredient
from skintellect.research.models import SearchIntent


def interpret_baseline(query):
    """Transparent offline baseline. Unsupported requests stay unresolved and block execution."""
    q = query.casefold()
    intent = SearchIntent(text=query)
    categories = {'moisturizer': 'moisturizers', 'moisturiser': 'moisturizers', 'cream': 'moisturizers',
                  'cleanser': 'cleansers', 'toner': 'toners', 'serum': 'serums', 'sunscreen': 'sunscreens',
                  'shampoo': 'shampoos', 'conditioner': 'conditioners'}
    matched = {v for k, v in categories.items() if k in q}
    if len(matched) == 1:
        intent.category = matched.pop()
    elif len(matched) > 1:
        intent.unresolved_terms.append('Multiple categories: choose one in the structured filters.')
    if any(t in q for t in ('shampoo', 'conditioner', 'hair')):
        intent.domain = 'hair'
    if re.search(r'(?:fragrance|perfume)[ -]free|(?:no|without|exclude)\s+(?:fragrance|perfume)', q):
        intent.excluded_ingredients.append('Parfum')
    if re.search(r'\bceramides?\b', q):
        intent.required_ingredients.append('ceramides')
    for ingredient in ('niacinamide', 'panthenol', 'glycerin', 'retinol', 'salicylic acid', 'dimethicone'):
        if ingredient in q:
            if re.search(r'(?:no|without|exclude)\s+' + re.escape(ingredient), q):
                intent.excluded_ingredients.append(ingredient)
            else:
                intent.required_ingredients.append(ingredient)
    if re.search(r'\b(lightweight|light texture|light moisturizer)\b', q):
        intent.preferences.append('lightweight')

    if re.search(r'\b(?:fungal[ -]?acne|malassezia)(?:[ -]safe)?\b', q):

        intent.preferences.append('fungal_acne_safe')

    if re.search(r'\boil[ -]free\b', q):

        intent.preferences.append('oil_free')
    if re.search(r'\b(cheap|cheaper|budget|affordable|lower price)\b', q):
        intent.preferred_price_tiers = ['$', '$$']
    if re.search(r'₹|\binr\b|\brupees?\b|\bunder\s+\d+', q):
        intent.unresolved_terms.append('Exact local prices are unavailable; choose a catalog price tier.')
    # Do not pretend the offline parser understands every exclusion or clinical request.
    covered = re.sub(r'(?:fragrance|perfume)[ -]free|(?:no|without|exclude)\s+(?:fragrance|perfume|niacinamide|panthenol|glycerin|retinol|salicylic acid|dimethicone)|\b(?:fungal[ -]?acne|malassezia)(?:[ -]safe)?\b|\boil[ -]free\b', '', q)
    if re.search(r'\b(no|without|exclude|free|allerg\w*|safe|pregnan\w*|treat\w*)\b', covered):
        intent.unresolved_terms.append('An unsupported safety or exclusion phrase needs explicit structured filters.')
    if not matched and intent.category == 'all' and not intent.required_ingredients and not intent.excluded_ingredients:
        intent.unresolved_terms.append('Choose a product category or ingredient constraint.')
    return {'intent': intent.model_dump(), 'mode': 'offline_rule_parser',
            'notice': 'Review the editable filters. This parser is a limited baseline, not an LLM.'}

def interpret(query, db_path=None):
    from skintellect.research.model_steps import extract_intent
    return extract_intent(query, interpret_baseline(query), get_catalog(db_path).path)

def eligibility(p, intent):
    checks = [check_ingredient(i, p['names'], p['complete']) for i in intent.required_ingredients]
    checks += [check_ingredient(i, p['names'], p['complete'], exclude=True) for i in intent.excluded_ingredients]
    eid = 'product:' + str(p['id'])
    for check in checks:
        check['evidence_ids'] = [eid] if check['matched_names'] or p['complete'] else []
    return checks

def brief(p):
    return {k: p.get(k) for k in ('id', 'brand', 'name', 'category', 'domain', 'price_tier', 'url')} | {
        'formula_status': 'verified_complete' if p['complete'] else ('unverified' if p['formula'] else 'missing'),
        'is_seed': bool(p.get('is_seed')), 'evidence_id': 'product:' + str(p['id']),
        'score_kind': 'heuristic_preference', 'formulation_version': 'unverified'}

def structured_search(intent, product_ids=None, records=None):
    if intent.unresolved_terms:
        return {'products': [], 'total': 0, 'unknown_count': 0, 'failed_count': 0,
                'intent': intent.model_dump(), 'needs_clarification': intent.unresolved_terms}
    found, unknown, failed = [], 0, 0
    for p in (records if records is not None else load_records()):
        if product_ids is not None and p['id'] not in product_ids:
            continue
        if p.get('is_seed') != 0:
            continue
        if intent.domain != 'all' and p.get('domain') != intent.domain:
            continue
        if intent.category != 'all' and intent.category.casefold().rstrip('s') not in (p.get('category') or '').casefold():

            continue

        if 'fungal_acne_safe' in intent.preferences and p.get('fungal_acne_safe', 0) == 0:

            continue

        if 'oil_free' in intent.preferences and p.get('oil_free', 0) == 0:

            continue

        checks = eligibility(p, intent)
        if any(c['status'] == 'fail' for c in checks):
            failed += 1
            continue
        if any(c['status'] == 'unknown' for c in checks):
            unknown += 1
            continue
        tier_score = int(p.get('price_tier') in intent.preferred_price_tiers) if intent.preferred_price_tiers else 0
        found.append(brief(p) | {'checks': checks, 'ranking_components': {'price_preference': tier_score},
                                'unresolved_preferences': intent.preferences})
    found.sort(key=lambda p: (-p['ranking_components']['price_preference'], p['id']))
    return {'products': found[:intent.limit], 'total': len(found), 'unknown_count': unknown,
            'failed_count': failed, 'intent': intent.model_dump(), 'needs_clarification': [],
            'notice': 'Unknown exclusions are withheld. Price tiers are approximate. Texture preferences are not yet ranked.'}
