"""Behavior checks across the approved deepened modules, using real disposable SQLite."""
import json
import os
import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from skintellect.catalog.store import Catalog, catalog_scope, get_catalog
from skintellect.database import database
from skintellect.formulation.ingredient_facts import classify_ingredients
from skintellect.gemini import GeminiClient, ensure_tables
from skintellect.research import jobs
from skintellect.research.passage_index import PassageIndex
from skintellect.research.preparation import prepare_reviews
from skintellect.research.retrieval import corpus, index_embeddings
from skintellect.research.review_store import ReviewCorpus
from skintellect.research.reviews import review_insights
from tests import test_research as fixtures


class ArchitectureBehaviorTests(unittest.TestCase):
    def setUp(self):
        fixtures.ResearchTests.setUp(self)
        self.settings = patch.dict(os.environ, {
            'RESEARCH_LLM_ENABLED': '1', 'GEMINI_BACKEND': 'developer',
            'GEMINI_API_KEY': 'synthetic-only', 'GEMINI_MODEL': 'deepening-test',
            'GEMINI_ABSA_MODEL': 'deepening-test',
            'GEMINI_EMBEDDING_MODEL': 'gemini-embedding-001',
        })
        self.settings.start()
        self.addCleanup(self.settings.stop)
        ensure_tables(self.path)

    def tearDown(self):
        fixtures.ResearchTests.tearDown(self)

    def test_corrupt_current_vector_is_unready_and_repaired(self):
        doc = next(d for d in corpus(self.path) if d['evidence_id'] == 'review:1')
        client = GeminiClient(self.path)
        with database(self.path) as connection:
            connection.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',
                (doc['evidence_id'], client.embedding_model, doc['content_hash'],
                 client.embedding_dimensions, '[0]'))
        self.assertEqual(jobs.snapshot(self.path)['embeddings']['indexed'], 0)
        vector = [1.] + [0.] * (client.embedding_dimensions - 1)
        with patch.object(GeminiClient, 'embed', return_value=[vector]) as embed:
            result = index_embeddings(self.path, evidence_ids=['review:1'])
        self.assertEqual(result['indexed'], 1)
        embed.assert_called_once()
        self.assertEqual(jobs.snapshot(self.path)['embeddings']['indexed'], 1)

    def test_vector_batch_validation_is_atomic(self):
        client = GeminiClient(self.path)
        docs = corpus(self.path)[:2]
        index = PassageIndex(self.path, client.embedding_model, client.embedding_dimensions)
        good = [1.] + [0.] * (client.embedding_dimensions - 1)
        for bad in ([0.] * client.embedding_dimensions, [True] + good[1:], {'bad': 1}, None):
            with self.subTest(payload=type(bad).__name__):
                with self.assertRaises(ValueError):
                    index.save(docs, [good, bad])
                self.assertEqual(index.read(docs).vectors, {})

    def test_corrupt_review_is_not_counted_or_displayed_and_is_reprepared(self):
        store = ReviewCorpus(self.path)
        source = store.read(product_ids=[1])[0]
        invalid = {'aspect': 'hydration', 'sentiment': 'positive', 'negated': False,
                   'span': 'Invented quote', 'start': 0, 'end': 9}
        with database(self.path) as connection:
            connection.execute('INSERT INTO review_aspects VALUES(?,?,?,?)',
                (source['id'], source['input_hash'], store.version('deepening-test'), json.dumps([invalid])))
        self.assertEqual(jobs.snapshot(self.path)['reviews']['processed'], 0)
        self.assertEqual(review_insights(1)['gemini_reviews'], 0)
        with patch('skintellect.research.model_steps.analyze_review_batch',
                   return_value={source['id']: source['baseline']}) as extraction:
            result = prepare_reviews(self.path, product_id=1)
        extraction.assert_called_once()
        self.assertEqual(result['processed_reviews'], 1)
        self.assertEqual(jobs.snapshot(self.path)['reviews']['processed'], 1)
        self.assertEqual(review_insights(1)['gemini_reviews'], 1)
        with patch.dict(os.environ, {'GEMINI_ABSA_MODEL': 'other-model'}):
            self.assertEqual(jobs.snapshot(self.path)['reviews']['processed'], 0)

    def test_review_identity_is_product_scoped_and_keeps_raw_evidence_ids(self):
        with database(self.path) as connection:
            connection.execute("INSERT INTO reviews VALUES(3,3,?,'','2026')",
                               ("Hydrating, but sticky. Didn't sting. Show more",))
        store = ReviewCorpus(self.path)
        unique = store.read()
        self.assertEqual([r['id'] for r in unique], [1, 3])
        self.assertEqual([r['id'] for r in store.read(unique=False)], [1, 2, 3])
        self.assertEqual({d['evidence_id'] for d in corpus(self.path) if d['kind'] == 'reported_experience'},
                         {'review:1', 'review:2', 'review:3'})

    def test_classification_preserves_profiles_and_unknown_source_ratings(self):
        ingredients = [{'name': 'Glycerin'}, {'name': 'Colloidal Oatmeal'},
                       {'name': 'Centella Asiatica'}, {'name': 'Unobtainium', 'is_pore_clogging': True}]
        formula = classify_ingredients(ingredients)
        report = classify_ingredients(ingredients, profile='recommendation')
        catalog = classify_ingredients(ingredients, profile='catalog')
        self.assertIn('Glycerin', formula.groups['barrier'])
        self.assertNotIn('Glycerin', report.groups['hydrators'])
        self.assertIn('Colloidal Oatmeal', formula.groups['smoothers'])
        self.assertNotIn('Colloidal Oatmeal', report.groups['smoothers'])
        self.assertIn('Centella Asiatica', catalog.groups['smoothers'])
        self.assertNotIn('Unobtainium', formula.groups['cloggers'])
        self.assertIn('Unobtainium', catalog.groups['pore_cloggers'])
        self.assertIsNone(formula.provided_flags[0]['comedogenic'])

    def test_catalog_scopes_isolate_cache_and_restore_selection(self):
        original = get_catalog()
        self.assertEqual(original.display_records()[0]['name'], 'Product 1')
        other_path = Path(self.temp.name) / 'other.db'
        with closing(sqlite3.connect(self.path)) as source, closing(sqlite3.connect(other_path)) as target:
            source.backup(target)
        with database(other_path) as connection:
            connection.execute("UPDATE products SET name='Other catalog' WHERE id=1")
        other = Catalog(other_path)
        with self.assertRaisesRegex(RuntimeError, 'restore'):
            with catalog_scope(other):
                self.assertEqual(get_catalog().display_records()[0]['name'], 'Other catalog')
                raise RuntimeError('restore')
        self.assertIs(get_catalog(), original)
        self.assertEqual(get_catalog().display_records()[0]['name'], 'Product 1')
        self.assertEqual(get_catalog(other_path).display_records()[0]['name'], 'Other catalog')
        self.assertIs(get_catalog(), original)

    def test_fresh_records_share_changed_formula_facts(self):
        catalog = get_catalog(self.path)
        catalog.display_records()
        with database(self.path) as connection:
            connection.execute('UPDATE products SET ingredients_json=? WHERE id=1',
                               (json.dumps(['Water', 'Retinol']),))
            connection.execute('UPDATE products SET ingredients_json=? WHERE id=3',
                               (json.dumps(['Water', 'Salicylic Acid']),))
        fresh = {r['id']: r for r in catalog.records()}
        shown = {r['id']: r for r in catalog.display_records()}
        self.assertEqual(fresh[1]['names'], shown[1]['names'])
        self.assertFalse(shown[1]['complete'])
        self.assertEqual(shown[1]['formula_status'], 'unverified')


if __name__ == '__main__':
    unittest.main()
