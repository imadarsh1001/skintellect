import unicodedata

"""Ingredient matching facts with explicit legacy presentation policies, not score formulas."""
import re
from dataclasses import dataclass

FUNGAL_ACNE_TRIGGERS = [
    r'\bpolysorbate\b', r'\blauric acid\b', r'\bmyristic acid\b', r'\bpalmitic acid\b',
    r'\bstearic acid\b', r'\boleic acid\b', r'\blinoleic acid\b', r'\blinolenic acid\b',
    r'\bisopropyl myristate\b', r'\bisopropyl palmitate\b', r'\bcetyl palmitate\b',
    r'\bglyceryl stearate\b', r'\bsorbitan oleate\b', r'\bsorbitan stearate\b',
    r'\bgalactomyces\b', r'\bpeg-100 stearate\b',
    r'\bpolyglyceryl-[0-9]+\s*(?:di|tri|poly)?(?:stearate|oleate|palmitate|myristate|isostearate|distearate)\b',
    r'\bceteareth-20\b', r'\bcetearyl olivate\b', r'\bsorbitan olivate\b',
    r'\bethylhexyl palmitate\b', r'\bethylhexyl stearate\b'
]


BRIGHTENERS = [
    r'\bniacinamide\b', r'\btranexamic acid\b', r'\balpha-arbutin\b', r'\barbutin\b',
    r'\bascorbic acid\b', r'\bascorbyl glucoside\b', r'\bsodium ascorbyl phosphate\b',
    r'\b3-o-ethyl ascorbic acid\b', r'\bmagnesium ascorbyl phosphate\b',
    r'\bglycyrrhiza glabra\b', r'\bdipotassium glycyrrhizate\b', r'\blicorice\b',
    r'\bglutathione\b', r'\bkojic acid\b', r'\bazelaic acid\b'
]


BARRIER_HYDRATORS = [
    r'\bceramide\b', r'\bphytosphingosine\b', r'\bcholesterol\b',
    r'\bhyaluronic acid\b', r'\bsodium hyaluronate\b', r'\bhydrolyzed hyaluronic acid\b',
    r'\bhydrolyzed sodium hyaluronate\b', r'\bpanthenol\b', r'\bsqualane\b',
    r'\bbeta-glucan\b', r'\bpolyglutamic acid\b', r'\bcentella asiatica\b',
    r'\bmadecassoside\b', r'\basiaticoside\b', r'\bmadecassic acid\b',
    r'\basiatic acid\b', r'\ballantoin\b', r'\bectoin\b', r'\bglycerin\b'
]


SMOOTHERS_TEXTURE = [
    r'\bgluconolactone\b', r'\blactobionic acid\b', r'\bbifida ferment\b',
    r'\bsalicylic acid\b', r'\bcapryloyl salicylic acid\b', r'\bbetaine salicylate\b',
    r'\bzinc pca\b', r'\bsuccinic acid\b', r'\bavena sativa\b', r'\bcolloidal oatmeal\b',
    r'\boat extract\b', r'\boat kernel\b'
]


IRRITANTS_ALLERGENS = [
    r'\bfragrance\b', r'\bparfum\b', r'\blimonene\b', r'\blinalool\b',
    r'\bcitronellol\b', r'\bgeraniol\b', r'\beugenol\b', r'\bcinnamal\b',
    r'\bcitral\b', r'\bbenzyl alcohol\b', r'\blavandula angustifolia\b',
    r'\blavender oil\b', r'\bcitrus limon\b', r'\bcitrus aurantium\b',
    r'\bmentha piperita\b', r'\beucalyptus globulus\b', r'\balcohol denat\b',
    r'\bsd alcohol\b', r'\bpeppermint oil\b'
]


KNOWN_PORE_CLOGGERS = [
    r'\bcetearyl alcohol\b', r'\bcetyl alcohol\b', r'\bcocos nucifera\b',
    r'\bcoconut oil\b', r'\btheobroma cacao\b', r'\bcocoa butter\b',
    r'\bethylhexyl palmitate\b', r'\bisopropyl myristate\b', r'\bisopropyl isostearate\b',
    r'\bmyristyl myristate\b', r'\blaureth-4\b', r'\bpotassium chloride\b',
    r'\bwheat germ oil\b', r'\bsoybean oil\b', r'\bcorn oil\b'
]


@dataclass
class IngredientFacts:
    groups: dict
    provided_flags: list


def classify_ingredients(ingredients, profile='formula'):
    """Preserve each caller's classification policy and separate provided flags from matches."""
    if profile not in {'formula', 'catalog', 'recommendation'}:
        raise ValueError('unknown_ingredient_profile')
    patterns = {'brighteners': BRIGHTENERS, 'hydrators': BARRIER_HYDRATORS,
                'smoothers': SMOOTHERS_TEXTURE, 'irritants': IRRITANTS_ALLERGENS}
    if profile == 'formula':
        patterns['fungal_triggers'] = FUNGAL_ACNE_TRIGGERS
        patterns['pore_cloggers'] = KNOWN_PORE_CLOGGERS
    elif profile == 'recommendation':
        # Preserve historical report behavior; changing its policy is separate from consolidation.
        patterns['hydrators'] = [p for p in BARRIER_HYDRATORS if p != r'\bglycerin\b']
        patterns['smoothers'] = [p.replace('colloidal', 'collodial') for p in SMOOTHERS_TEXTURE] + [r'\bgalactomyces\b']
        patterns['pore_cloggers'] = []
    else:
        patterns = {
            'brighteners': [r'\b(niacinamide|tranexamic|arbutin|ascorb|glycyrrhizate|licorice|glutathione|kojic|azelaic)\b'],
            'hydrators': [r'\b(ceramide|phytosphingosine|cholesterol|hyaluronic|squalane|panthenol|beta-glucan|ectoin|glycerin)\b'],
            'smoothers': [r'\b(gluconolactone|lactobionic|bifida|salicylic|zinc pca|succinic|avena|oatmeal|centella|madecassoside)\b'],
            'pore_cloggers': [r'\b(cetearyl alcohol|coconut oil|cocoa butter|ethylhexyl palmitate|isopropyl myristate|laureth-4)\b'],
        }
    groups = {key: [] for key in patterns}
    provided = []
    for ingredient in ingredients or []:
        record = ingredient if isinstance(ingredient, dict) else {'name': str(ingredient)}
        name = record.get('name', '')
        provided.append({'name': name, 'comedogenic': record.get('comedogenic'),
                         'is_pore_clogging': record.get('is_pore_clogging')})
        for group, rules in patterns.items():
            matched = any(re.search(rule, name.lower()) for rule in rules)
            if group == 'pore_cloggers' and profile != 'formula':
                matched = matched or bool(record.get('is_pore_clogging'))
                if profile == 'recommendation':
                    matched = matched or (record.get('comedogenic') or 0) >= 3
            if matched:
                label = f"{name} (Comedogenic: {record.get('comedogenic') or 0})" if group == 'pore_cloggers' and profile == 'recommendation' else name
                if profile == 'catalog' or group == 'pore_cloggers' and profile == 'recommendation' or label not in groups[group]:
                    groups[group].append(label)
    if profile == 'formula':
        groups['barrier'] = groups.pop('hydrators')
        groups['cloggers'] = groups.pop('pore_cloggers')
    return IngredientFacts(groups, provided)


ALIASES = {"aqua": "water", "aqua water": "water", "water aqua": "water",
           "fragrance": "parfum", "perfume": "parfum", "glycerine": "glycerin"}


def normalize(value):
    key = re.sub(r"[^\w\s/-]", " ", unicodedata.normalize("NFKC", value).casefold())
    key = " ".join(key.split())
    return ALIASES.get(key, key)


def names_from_formula(items):
    return [normalize(i.get("name", "") if isinstance(i, dict) else str(i)) for i in items]
