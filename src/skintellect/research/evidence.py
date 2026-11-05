import re

from skintellect.formulation.ingredient_facts import normalize

RULE_VERSION = "foundation-1"


FRAGRANCE = {"parfum", "linalool", "limonene", "geraniol", "citronellol", "eugenol", "citral"}



def ingredient_matches(query, names):
    key = normalize(query)
    if key in {"ceramide", "ceramides"}:
        return [n for n in names if re.match(r"^ceramide(?:\s|$)", n)]
    if key == "parfum":
        return [n for n in names if n in FRAGRANCE]
    return [n for n in names if n == key]

def check_ingredient(query, names, complete=False, exclude=False):
    found = ingredient_matches(query, names)
    status = ("fail" if exclude else "pass") if found else (
        ("pass" if exclude else "fail") if complete else "unknown")
    return {"constraint": ("exclude:" if exclude else "require:") + query,
            "status": status, "matched_names": found,
            "reason": "Observed in recorded formula" if found else (
                "Absent from verified complete formula" if complete else "Formula completeness is unverified")}

import sqlite3

from skintellect.database import database


def evidence(evidence_id, db_path=None):
    from skintellect.catalog.store import get_catalog
    db_path = get_catalog(db_path).path
    from skintellect.research.review_store import extract_review
    kind, _, identifier = evidence_id.partition(':')
    if kind=='source':
        from skintellect.research.references import references
        return next((r for r in references(db_path) if r['evidence_id']==evidence_id),None)
    if not identifier.isdigit():
        return None
    with database(db_path) as c:
        c.row_factory = sqlite3.Row
        if kind == 'product':
            row = c.execute('SELECT id,url,ingredients_json,description FROM products WHERE id=?', (int(identifier),)).fetchone()
            return dict(row) | {'kind': 'catalog_record', 'verification': 'source_attributed_only'} if row else None
        if kind == 'review':
            row = c.execute('SELECT id,product_id,review_text,date_posted FROM reviews WHERE id=?', (int(identifier),)).fetchone()
            if row:
                return dict(row) | {'kind': 'reported_experience', 'cleaned_text': extract_review(row['review_text'])[0],
                                     'formulation_match': 'unverified'}
    return None
