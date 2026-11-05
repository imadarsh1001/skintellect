import skintellect.research.alternatives as alternative_tools
import skintellect.research.evidence as evidence_tools
import skintellect.research.retrieval as retrieval_tools
import skintellect.research.reviews as review_tools
import skintellect.research.search as search_tools
from skintellect.research.review_store import extract_review

"""Contract, regression and HTTP checks using isolated synthetic data, never live catalog edits."""
import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from skintellect.database import database, formula_hash, migrate
from skintellect.formulation.ingredient_facts import normalize
from skintellect.research import service
from skintellect.research.evidence import check_ingredient
from skintellect.research.models import SearchIntent


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {'RESEARCH_LLM_ENABLED': '0'})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        test_root = Path(os.environ.get("SKINTELLECT_TEST_TEMP", str(Path.cwd() / ".test-work")))
        test_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=test_root, prefix="fixture-")
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / 'fixture.db')
        with database(self.path) as c:
            c.executescript('''CREATE TABLE products(id INTEGER PRIMARY KEY,brand TEXT,name TEXT,category TEXT,
                domain TEXT,price_tier TEXT,url TEXT,description TEXT,ingredients_json TEXT);
                CREATE TABLE reviews(id INTEGER PRIMARY KEY,product_id INTEGER,review_text TEXT,
                reviewer_skin_type TEXT,date_posted TEXT);''')
            formulas = [ ['Water', 'Ceramide NP', 'Panthenol'], ['Aqua', 'Ceramide NP', 'Parfum'],
                         ['Water', 'Ceramide NP', 'Glycerin'], [], ['Water', 'Ceramide NP'] ]
            for pid, names in enumerate(formulas, 1):
                c.execute('INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?)',
                    (pid, 'Test', 'Product ' + str(pid), 'Moisturizers', 'skin', '$', '', 'Marketing claims',
                     json.dumps([{'name': n} for n in names])))
            c.execute('INSERT INTO reviews VALUES(1,1,?,?,?)', ("Hydrating, but sticky. Didn't sting. Show more", 'sensitive', '2025'))
            c.execute('INSERT INTO reviews VALUES(2,1,?,?,?)', ("Hydrating, but sticky. Didn't sting. Show more", 'sensitive', '2025'))
            for column, declaration in [('image_url', "TEXT DEFAULT ''"), ('match_score', 'INTEGER DEFAULT 100'),
                                        ('rating', 'REAL DEFAULT 0'), ('review_count', 'INTEGER DEFAULT 0')]:
                c.execute('ALTER TABLE products ADD COLUMN ' + column + ' ' + declaration)
            c.executescript('''CREATE TABLE ingredients(id INTEGER PRIMARY KEY,skinsort_id INTEGER,
                name TEXT,slug TEXT,function TEXT,description TEXT,comedogenic INTEGER,irritancy INTEGER,
                is_pore_clogging INTEGER,fungal_trigger TEXT,benefits_json TEXT,domains_json TEXT,sources_json TEXT);
                CREATE TABLE product_ingredients(product_id INTEGER,ingredient_id INTEGER,
                is_key_ingredient INTEGER,key_note TEXT);''')
            c.execute("INSERT INTO ingredients VALUES(1,1,'Water','water','Solvent','',NULL,NULL,0,'','[]','[\"skin\"]','[\"skintellect\"]')")
        migrate(self.path)
        with database(self.path) as c:
            raw = c.execute('SELECT ingredients_json FROM products WHERE id=1').fetchone()[0]
            c.execute("UPDATE record_quality SET formula_status='verified_complete',verified_hash=?,verified_source='test label',verified_at='2026' WHERE product_id=1", (formula_hash(json.loads(raw)),))
            c.execute('UPDATE record_quality SET is_seed=1 WHERE product_id=5')
        from contextlib import ExitStack

        from skintellect.catalog.store import catalog_scope
        self.override = ExitStack()
        self.addCleanup(self.override.close)
        self.override.enter_context(catalog_scope(self.path))

    def tearDown(self):
        self.override.close()
        self.environment.stop()
        self.temp.cleanup()

    def test_alias_exact_identity(self):
        self.assertEqual(normalize(' Aqua (Water) '), 'water')
        self.assertEqual(check_ingredient('Water', ['water'])['status'], 'pass')
        self.assertEqual(check_ingredient('alcohol', ['cetearyl alcohol'])['status'], 'unknown')

    def test_fragrance_policy_detects_allergen(self):
        self.assertEqual(check_ingredient('Parfum', ['limonene'], exclude=True)['status'], 'fail')

    def test_unknown_exclusion_withheld(self):
        result = search_tools.structured_search(SearchIntent(excluded_ingredients=['Parfum']))
        self.assertEqual([p['id'] for p in result['products']], [1])
        self.assertEqual(result['failed_count'], 1)
        self.assertEqual(result['unknown_count'], 2)

    def test_required_presence_does_not_need_absence_verification(self):
        result = search_tools.structured_search(SearchIntent(required_ingredients=['ceramides']))
        self.assertEqual({p['id'] for p in result['products']}, {1, 2, 3})

    def test_seed_excluded(self):
        self.assertNotIn(5, [p['id'] for p in search_tools.structured_search(SearchIntent())['products']])

    def test_changed_formula_invalidates_verification(self):
        with database(self.path) as c:
            c.execute("UPDATE products SET ingredients_json='[]' WHERE id=1")
        result = search_tools.structured_search(SearchIntent(excluded_ingredients=['Parfum']))
        self.assertFalse(result['products'])

    def test_verification_requires_provenance(self):
        with database(self.path) as c:
            c.execute('UPDATE record_quality SET verified_source=NULL WHERE product_id=1')
        self.assertFalse(search_tools.structured_search(SearchIntent(excluded_ingredients=['Parfum']))['products'])

    def test_no_constraint_relaxation(self):
        result = search_tools.structured_search(SearchIntent(required_ingredients=['Unobtainium']))
        self.assertFalse(result['products'])

    def test_review_negation_and_mixed_sentiment(self):
        cleaned, rows = extract_review("Hydrating, but sticky. Didn't sting.")
        self.assertEqual([o['sentiment'] for o in rows], ['positive', 'negative', 'positive'])
        self.assertTrue(rows[-1]['negated'])
        for o in rows:
            self.assertEqual(cleaned[o['start']:o['end']], o['span'])

    def test_review_dedup_truncation(self):
        result = review_tools.review_insights(1)
        self.assertEqual(result['unique_reviews'], 1)
        self.assertEqual(result['duplicates_removed'], 1)
        self.assertTrue(all(o['truncated'] for o in result['observations']))

    def test_review_cache_invalidates_on_text_edit(self):
        review_tools.review_insights(1)
        with database(self.path) as c:
            c.execute("UPDATE reviews SET review_text='Very heavy.'")
        result = review_tools.review_insights(1)
        self.assertEqual({o['aspect'] for o in result['observations']}, {'texture'})

    def test_alternatives_constraints_and_shared_ingredients(self):
        result = alternative_tools.alternatives(3, SearchIntent(excluded_ingredients=['Parfum']))
        self.assertEqual([p['id'] for p in result['alternatives']], [1])
        self.assertIn('ceramide np', result['alternatives'][0]['shared_ingredients'])

    def test_retrieval_ids_resolve(self):
        for d in retrieval_tools.retrieve('hydrating ceramides')['documents']:
            self.assertIsNotNone(evidence_tools.evidence(d['evidence_id']))

    def test_review_evidence_does_not_expose_author(self):
        self.assertNotIn('author', evidence_tools.evidence('review:1'))

    def test_missing_evidence(self):
        self.assertIsNone(evidence_tools.evidence('review:999'))
        self.assertIsNone(evidence_tools.evidence("review:1 OR 1=1"))

    def test_unsupported_price_blocks(self):
        result = service.assistant_query('Moisturizer under ₹800')
        self.assertTrue(result['search']['needs_clarification'])
        self.assertFalse(result['search']['products'])

    def test_unsupported_exclusion_blocks(self):
        parsed = search_tools.interpret('Moisturizer without essential oils')
        self.assertTrue(parsed['intent']['unresolved_terms'])

    def test_offline_workflow_trace(self):
        result = service.assistant_query('moisturizer with ceramides')
        self.assertEqual(result['trace']['model_calls'], 0)
        self.assertEqual(result['trace']['retries'], 0)
        self.assertTrue(result['search']['products'])

    def test_migration_idempotent(self):
        migrate(self.path)
        with database(self.path) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM foundation_migrations').fetchone()[0], 1)

    def test_assistant_uses_explicit_database_across_extracted_modules(self):
        from skintellect.catalog.store import catalog_scope
        other = Path(self.temp.name) / 'must-not-be-read.db'
        other.touch()
        with catalog_scope(other):
            result = service.assistant_query('moisturizer with ceramides', planning_mode='fixed', db_path=self.path)
        self.assertTrue(result['search']['products'])
        self.assertTrue(result['review_insights'])
        self.assertEqual(other.stat().st_size, 0)

    @unittest.skipIf(os.environ.get('SKINTELLECT_SKIP_HTTP') == '1', 'Sandbox loopback sockets are unavailable; run this test locally.')
    def test_http_contracts(self):
        from skintellect.api.app import app
        async def exercise():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as c:
                self.assertEqual((await c.get('/research')).status_code, 200)
                self.assertEqual((await c.post('/api/search', json={'limit': 1000})).status_code, 422)
                self.assertEqual((await c.get('/api/evidence/review:999')).status_code, 404)
                r = await c.post('/api/search', json={'excluded_ingredients': ['Parfum']})
                self.assertEqual(r.status_code, 200)
                self.assertEqual([p['id'] for p in r.json()['products']], [1])
        asyncio.run(exercise())

    def test_route_registration_and_validation(self):
        from fastapi import HTTPException

        from skintellect.api.app import app
        from skintellect.api.research import evidence, reviews, search
        schema = app.openapi()
        self.assertIn('/api/assistant/query', schema['paths'])
        self.assertEqual(search(SearchIntent(excluded_ingredients=['Parfum']))['total'], 1)
        self.assertEqual(reviews(1)['unique_reviews'], 1)
        with self.assertRaises(HTTPException) as err:
            evidence('review:999')
        self.assertEqual(err.exception.status_code, 404)

    def test_legacy_formula_serializes_unknown(self):
        from skintellect.formulation.formulas import analyze_formula_full
        from skintellect.formulation.models import FormulaLabResponse
        result = FormulaLabResponse(**analyze_formula_full('Unobtainium Extract'))
        self.assertIsNone(result.ingredients_breakdown[0].comedogenic)
        self.assertEqual(result.ingredients_breakdown[0].safety_status, 'unknown')
        self.assertIsNone(result.is_fungal_safe)

    def test_legacy_catalog_excludes_seeds(self):
        from skintellect.catalog.models import PaginatedProductsResponse
        from skintellect.catalog.products import get_products
        result = PaginatedProductsResponse(**get_products(limit=100))
        self.assertTrue(result.products)
        self.assertTrue(all(not p.is_seed for p in result.products))

    def test_source_profiles_do_not_claim_verification(self):
        from skintellect.catalog.ingredients import get_ingredient_detail, get_ingredients
        from skintellect.catalog.models import IngredientDetail
        first = get_ingredients(limit=1)['ingredients'][0]
        detail = IngredientDetail(**get_ingredient_detail(first['id']))
        self.assertTrue(all(not p['verified'] for p in detail.source_profiles.values()))


if __name__ == '__main__':
    unittest.main()
