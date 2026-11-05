import hashlib
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import ValidationError

from skintellect.database import database
from skintellect.gemini import GeminiClient, GeminiUnavailable
from skintellect.research import reviews as review_tools
from skintellect.research.model_steps import REVIEW_VERSION, analyze_review_batch
from skintellect.research.models import ReviewExtraction, ReviewObservation
from tests import test_research as fixtures


class DynamicDecisionTests(unittest.TestCase):
    def setUp(self):
        fixtures.ResearchTests.setUp(self)
        self.models = patch.dict(os.environ, {
            'RESEARCH_LLM_ENABLED': '1',
            'GEMINI_BACKEND': 'developer',
            'GEMINI_API_KEY': 'synthetic-only',
            'GEMINI_MODEL': 'dynamic-test',
            'GEMINI_ABSA_MODEL': 'dynamic-test',
            'GEMINI_EMBEDDING_MODEL': 'gemini-embedding-001',
        })
        self.models.start()
        self.addCleanup(self.models.stop)

    def tearDown(self):
        fixtures.ResearchTests.tearDown(self)

    def extraction(self, aspect='packaging', quote='The pump broke.'):
        return ReviewExtraction(observations=[
            ReviewObservation(
                review_id=1, aspect=aspect, sentiment='negative', negated=False, quote=quote
            )
        ])

    def test_new_aspects_normalized_without_forcing_known_taxonomy(self):
        o = self.extraction('Packaging / Pump').observations[0]
        self.assertEqual(o.aspect, 'packaging_pump')
        self.assertEqual(self.extraction('White Cast').observations[0].aspect, 'white_cast')
        self.assertEqual(self.extraction('fragrance').observations[0].aspect, 'scent')
        with self.assertRaises(ValidationError):
            self.extraction('!!!')
        with self.assertRaises(ValidationError):
            self.extraction('a' * 65)

    def test_open_aspect_extraction_preserves_exact_source(self):
        with patch.object(GeminiClient, 'structured', return_value=self.extraction()):
            output = analyze_review_batch([{'id': 1, 'cleaned_text': 'The pump broke.'}], self.path)[1][0]
        self.assertEqual(output['aspect'], 'packaging')
        self.assertTrue(output['is_discovered_aspect'])
        self.assertEqual('The pump broke.'[output['start']:output['end']], output['span'])

    def test_open_aspects_do_not_bypass_quote_validation(self):
        with patch.object(GeminiClient, 'structured', return_value=self.extraction()):
            with self.assertRaisesRegex(GeminiUnavailable, 'evidence_validation'):
                analyze_review_batch([{'id': 1, 'cleaned_text': 'The pump worked.'}], self.path)

    def test_new_aspect_is_in_summary_not_only_raw_observations(self):
        raw = 'The pump broke.'
        observation = {
            'aspect': 'packaging',
            'sentiment': 'negative',
            'negated': False,
            'span': raw,
            'start': 0,
            'end': len(raw),
            'is_discovered_aspect': True,
        }
        with database(self.path) as c:
            c.execute('UPDATE reviews SET review_text=? WHERE id=1', (raw,))
            c.execute(
                'INSERT INTO review_aspects VALUES(?,?,?,?)',
                (1, hashlib.sha256(raw.encode()).hexdigest(), REVIEW_VERSION + ':dynamic-test', json.dumps([observation])),
            )
        result = review_tools.review_insights(1)
        summary = next(a for a in result['aspects'] if a['aspect'] == 'packaging')
        self.assertEqual(summary['mentioning_reviews'], 1)
        self.assertTrue(summary['is_discovered_aspect'])

    def test_embedding2_sdk_preserves_cloud_credentials_and_dimensions(self):
        response = SimpleNamespace(
            embeddings=[SimpleNamespace(values=[3.0, 4.0] + [0.0] * 126)],
            usage_metadata=SimpleNamespace(prompt_token_count=7, total_token_count=7),
        )
        with patch.dict(os.environ, {
            'GEMINI_BACKEND': 'vertex',
            'GOOGLE_CLOUD_PROJECT': 'test-project',
            'GEMINI_EMBEDDING_MODEL': 'gemini-embedding-2',
            'GEMINI_EMBEDDING_TRANSPORT': 'sdk',
        }):
            with patch('google.genai.Client') as factory:
                factory.return_value.__enter__.return_value.models.embed_content.return_value = response
                client = GeminiClient(self.path)
                vectors = client.embed(['one', 'two'], dimensions=128)
                self.assertEqual(len(vectors), 2)
                self.assertEqual(factory.call_count, 2)
                self.assertTrue(factory.call_args.kwargs['vertexai'])
                self.assertNotIn('api_key', factory.call_args.kwargs)
                call = factory.return_value.__enter__.return_value.models.embed_content.call_args
                self.assertEqual(call.kwargs['contents'], 'title: none | text: two')
                self.assertEqual(call.kwargs['config'].output_dimensionality, 128)
                self.assertAlmostEqual(sum(x * x for x in vectors[0]), 1)
                self.assertEqual(client.last_telemetry['attempts'], 2)
                self.assertEqual(client.last_telemetry['input_tokens'], 14)


if __name__ == '__main__':
    unittest.main()
