from skintellect.catalog.store import get_catalog

"""Source-preserving review parsing and cached aspect summaries."""

from skintellect.research.review_store import ASPECTS, EXTRACTION_VERSION, ReviewCorpus


def review_insights(product_id, db_path=None):
    from skintellect.config import llm_enabled
    from skintellect.research.model_steps import REVIEW_VERSION, review_client
    db_path = get_catalog(db_path).path
    gemini_version = REVIEW_VERSION + ':' + review_client(db_path).model
    store = ReviewCorpus(db_path)
    all_sources = store.read(product_ids=[product_id], unique=False, include_seeds=True)
    sources = [r for r in all_sources if r['cleaned_text'] and not r['duplicate']]
    baseline_cache = store.cached(None, sources).observations
    model_cache = store.cached(review_client(db_path).model, sources).observations if llm_enabled() else {}
    uncached = [r for r in sources if r['id'] not in baseline_cache]
    if uncached:
        store.save(None, uncached, {r['id']: r['baseline'] for r in uncached})
    observations = []
    for r in sources:
        extracted = model_cache.get(r['id'], baseline_cache.get(r['id'], r['baseline']))
        for item in extracted:
            observations.append(item | {'review_id': r['id'], 'evidence_id': 'review:' + str(r['id']),
                'skin_type': r.get('reviewer_skin_type'), 'truncated': 'show more' in r['raw_text'].casefold(),
                'formulation_match': 'unverified', 'quote': item.get('span', item.get('quote', ''))})
    model_review_count = len(model_cache)
    duplicate_count = sum(r['duplicate'] for r in all_sources if r['cleaned_text'])
    summaries = []
    aspect_names=list(ASPECTS)+sorted({o['aspect'] for o in observations}-set(ASPECTS))
    for aspect in aspect_names:
        items = [o for o in observations if o['aspect'] == aspect]
        if items:
            summaries.append({'aspect': aspect, 'is_discovered_aspect':aspect not in ASPECTS, 'mentioning_reviews': len({o['review_id'] for o in items}),
                'positive_reviews': len({o['review_id'] for o in items if o['sentiment'] == 'positive'}),
                'negative_reviews': len({o['review_id'] for o in items if o['sentiment'] == 'negative'}),
                'mixed_reviews': len({o['review_id'] for o in items if o['sentiment'] == 'mixed'}),
                'neutral_reviews': len({o['review_id'] for o in items if o['sentiment'] == 'neutral'})})
    return {'product_id': product_id, 'collected_reviews': len(all_sources), 'unique_reviews': len(sources),
            'duplicates_removed': duplicate_count, 'aspects': summaries, 'observations': observations,
            'extraction_version': gemini_version if model_review_count else EXTRACTION_VERSION,
            'mode': 'gemini_with_rule_fallback' if model_review_count else 'rule_baseline',
            'gemini_reviews': model_review_count,
            'notice': 'Counts describe collected reviews; categories may overlap. Formula version matching is unverified.'}
