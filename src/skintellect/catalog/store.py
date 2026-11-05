"""Selected catalog reads, common formula facts and per-catalog display cache lifetime."""
import json
import sqlite3
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from skintellect.config import DB_PATH
from skintellect.database import database, formula_hash
from skintellect.formulation.ingredient_facts import classify_ingredients, names_from_formula

# Category Slugs and Display Names
CATEGORIES = {
    "moisturizers": "Moisturizers",
    "sunscreens": "Sunscreens",
    "face-cleansers": "Cleansers",
    "cleansers": "Cleansers",
    "toners": "Toners",
    "serums": "Serums",
    "treatments": "Treatments",
    "exfoliators": "Exfoliators",
    "eye-care": "Eye Care",
}

PRICE_RANGES = {
    "$": "Budget (<$15)",
    "$$": "Moderate ($15-$30)",
    "$$$": "Premium ($30-$60)",
    "$$$$": "Luxury ($60+)",
}



class Catalog:
    def __init__(self, db_path):
        self.path = str(Path(db_path).resolve())
        if not Path(self.path).is_file():
            raise FileNotFoundError(self.path)
        self._display = None
        self._stamp = None

    @property
    def stamp(self):
        values = [self.path]
        for path in (Path(self.path), Path(self.path + '-wal')):
            if path.exists():
                stat = path.stat()
                header_counter = None
                try:
                    with open(path, 'rb') as f:
                        f.seek(24)
                        header_counter = f.read(4)
                except OSError:
                    pass
                values.append((stat.st_mtime_ns, stat.st_size, stat.st_ino, header_counter))
            else:
                values.append(None)
        return tuple(values)

    def _read(self, with_reviews=False):
        with database(self.path) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute('BEGIN')
            rows = [dict(r) for r in connection.execute('SELECT * FROM products ORDER BY id')]
            quality = {r['product_id']: dict(r) for r in connection.execute('SELECT * FROM record_quality')}
            reviews = [dict(r) for r in connection.execute('SELECT * FROM reviews ORDER BY date_posted DESC')] if with_reviews else []
        return rows, quality, reviews

    @staticmethod
    def _normalize(row, quality):
        record = dict(row)
        raw = record.get('ingredients_json')
        try:
            formula = json.loads(raw) if isinstance(raw, str) else raw
            if not isinstance(formula, list):
                formula = []
        except (ValueError, TypeError):
            formula = []
        complete = bool(formula and quality.get('formula_status') == 'verified_complete'
                        and quality.get('verified_hash') == formula_hash(formula)
                        and quality.get('verified_source') and quality.get('verified_at'))
        return record | quality | {'formula': formula, 'names': names_from_formula(formula),
            'complete': complete, 'is_seed': quality.get('is_seed'),
            'formula_status': 'verified_complete' if complete else 'unverified' if formula else 'missing',
            'score_kind': 'heuristic_preference'}

    def records(self):
        rows, quality, _ = self._read()
        return [self._normalize(r, quality.get(r['id'], {})) for r in rows]

    def display_records(self, refresh=False):
        stamp = self.stamp
        if not refresh and self._display is not None and self._stamp == stamp:
            return self._display
        rows, quality, reviews = self._read(with_reviews=True)
        reviews_by_pid = {}
        for review in reviews:
            if review.get('tags'):
                try:
                    review['tags'] = json.loads(review['tags'])
                except (ValueError, TypeError):
                    pass
            reviews_by_pid.setdefault(review['product_id'], []).append(review)
        catalog = []
        for r in rows:
            p = self._normalize(r, quality.get(r['id'], {}))
            # Parse JSON fields safely
            for json_col in ['badges', 'ingredients_json', 'skin_goals', 'community_survey', 'rating_breakdown', 'key_actives_json', 'key_benefits_summary']:
                val = p.get(json_col)
                if isinstance(val, str) and val.strip():
                    try:
                        p[json_col] = json.loads(val)
                    except Exception:
                        p[json_col] = [] if 'json' in json_col or json_col in ['badges', 'skin_goals', 'community_survey'] else {}
                elif val is None:
                    p[json_col] = [] if 'json' in json_col or json_col in ['badges', 'skin_goals', 'community_survey'] else {}

            p['reviews'] = reviews_by_pid.get(p['id'], [])
            p['key_actives'] = p.get('key_actives_json', [])
            p['key_benefits'] = p.get('key_benefits_summary', [])
            p['ingredients'] = p['formula']
            p['parsed_skin_goals'] = [g.get('name', '') if isinstance(g, dict) else str(g) for g in p.get('skin_goals', [])]

            # Standardize category_display across all products
            raw_cat = p.get('category') or 'Moisturizers'
            raw_cat_lower = raw_cat.lower()
            if 'cleanse' in raw_cat_lower:
                p['category_display'] = 'Cleansers'
            elif 'tone' in raw_cat_lower:
                p['category_display'] = 'Toners'
            elif 'serum' in raw_cat_lower:
                p['category_display'] = 'Serums'
            elif 'sun' in raw_cat_lower or 'spf' in raw_cat_lower:
                p['category_display'] = 'Sunscreens'
            elif 'moistur' in raw_cat_lower or 'cream' in raw_cat_lower or 'oil' in raw_cat_lower or 'lotion' in raw_cat_lower:
                p['category_display'] = 'Moisturizers'
            else:
                p['category_display'] = raw_cat

            p['analysis'] = classify_ingredients(p.get('ingredients', []), profile='catalog').groups

            # Similar products / dupes
            sim_raw = p.get('similar_products')
            if isinstance(sim_raw, str) and sim_raw.strip():
                try:
                    p['similar_products'] = json.loads(sim_raw)
                except Exception:
                    p['similar_products'] = []
            elif not isinstance(sim_raw, list):
                p['similar_products'] = []

            catalog.append(p)

        self._display = catalog
        self._stamp = stamp
        return catalog


_selected_catalog = ContextVar('selected_catalog', default=None)
_default_catalog = None


def get_catalog(db_path=None):
    global _default_catalog
    selected = _selected_catalog.get()
    if selected is not None and (db_path is None or str(Path(db_path).resolve()) == selected.path):
        return selected
    if db_path is not None:
        return Catalog(db_path)
    if _default_catalog is None or _default_catalog.path != str(Path(DB_PATH).resolve()):
        _default_catalog = Catalog(DB_PATH)
    return _default_catalog


@contextmanager
def catalog_scope(catalog):
    selected = catalog if isinstance(catalog, Catalog) else Catalog(catalog)
    token = _selected_catalog.set(selected)
    try:
        yield selected
    finally:
        _selected_catalog.reset(token)
