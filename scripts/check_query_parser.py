"""Developer-written parser smoke cases. These are not a human-reviewed held-out benchmark."""
import json

from skintellect.research.search import interpret_baseline

CASES = [
    ('fragrance-free moisturizer', 'moisturizers', ['Parfum'], [], False),
    ('moisturizer without perfume', 'moisturizers', ['Parfum'], [], False),
    ('serum with niacinamide', 'serums', [], ['niacinamide'], False),
    ('cleanser without niacinamide', 'cleansers', ['niacinamide'], [], False),
    ('moisturizer with ceramides', 'moisturizers', [], ['ceramides'], False),
    ('toner with panthenol', 'toners', [], ['panthenol'], False),
    ('sunscreen without dimethicone', 'sunscreens', ['dimethicone'], [], False),
    ('moisturizer with glycerin', 'moisturizers', [], ['glycerin'], False),
    ('serum with retinol', 'serums', [], ['retinol'], False),
    ('cleanser with salicylic acid', 'cleansers', [], ['salicylic acid'], False),
    ('moisturizer under ₹800', 'moisturizers', [], [], True),
    ('moisturizer under 800 rupees', 'moisturizers', [], [], True),
    ('moisturizer without essential oils', 'moisturizers', [], [], True),
    ('moisturizer alcohol-free', 'moisturizers', [], [], True),
    ('pregnancy safe moisturizer', 'moisturizers', [], [], True),
    ('serum and moisturizer', 'all', [], [], True),
    ('show me products', 'all', [], [], True),
    ('affordable moisturizer', 'moisturizers', [], [], False),
    ('lightweight moisturizer', 'moisturizers', [], [], False),
    ('shampoo fragrance-free', 'shampoos', ['Parfum'], [], False),
]


def run():
    results = []
    for query, category, excluded, required, blocked in CASES:
        intent = interpret_baseline(query)['intent']
        passed = (intent['category'] == category and intent['excluded_ingredients'] == excluded
                  and intent['required_ingredients'] == required and bool(intent['unresolved_terms']) == blocked)
        results.append({'query': query, 'passed': passed, 'intent': intent})
    return {'label': 'Developer smoke cases; no held-out accuracy claim', 'passed': sum(r['passed'] for r in results),
            'total': len(results), 'cases': results}


if __name__ == '__main__':
    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] == report['total'] else 1)
