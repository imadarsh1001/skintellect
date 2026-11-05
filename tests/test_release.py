"""Release provenance, cache boundaries, graph, MCP and label-reading contracts."""
import asyncio
import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

import httpx

from skintellect.database import database
from skintellect.gemini import GeminiClient, run_budget
from skintellect.research.connections import connections
from skintellect.research.references import ingest_references, references
from skintellect.research.study import readiness, save_evaluation, select_cohort
from tests import test_research as fixtures


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        fixtures.ResearchTests.setUp(self)
        self.env=patch.dict(os.environ,{'RESEARCH_LLM_ENABLED':'1','GEMINI_BACKEND':'developer',
            'GEMINI_API_KEY':'test-only','GEMINI_MODEL':'release-test','GEMINI_ABSA_MODEL':'release-test','GEMINI_EMBEDDING_MODEL':'gemini-embedding-001'})
        self.env.start()

    def tearDown(self):
        self.env.stop();fixtures.ResearchTests.tearDown(self)

    def prepared_fixture(self):
        from skintellect.research.model_steps import REVIEW_VERSION
        from skintellect.research.retrieval import corpus
        with database(self.path) as c:
            c.execute('UPDATE products SET ingredients_json=? WHERE id=1',
                (json.dumps([{'name':n} for n in ['Water','Ceramide NP','Panthenol']+['Ingredient '+str(i) for i in range(8)]]),))
            c.execute("UPDATE reviews SET review_text='Not sticky.' WHERE id=2")
            c.execute("INSERT INTO reviews VALUES(3,1,'Absorbs quickly.','','2026')")
        manifest=select_cohort(self.path)
        client=GeminiClient(self.path)
        with database(self.path) as c:
            for rid,raw in c.execute('SELECT id,review_text FROM reviews'):
                c.execute('INSERT INTO review_aspects VALUES(?,?,?,?)',
                    (rid,hashlib.sha256(raw.encode()).hexdigest(),REVIEW_VERSION+':'+client.model,'[]'))
            for d in corpus(self.path):
                if d['product_id'] in manifest['product_ids']:
                    c.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',
                        (d['evidence_id'],client.embedding_model,d['content_hash'],768,json.dumps([1.]+[0.]*767)))
        return manifest

    def test_cohort_freshness_and_corrupt_vectors(self):
        manifest=self.prepared_fixture()
        self.assertEqual(manifest['product_ids'],[1])
        ready=readiness(self.path);self.assertTrue(ready['ready'])
        save_evaluation(self.path,{'input_fingerprint':ready['input_fingerprint']})
        self.assertTrue(readiness(self.path)['evaluation_current'])
        with database(self.path) as c:c.execute("UPDATE products SET description='Changed source' WHERE id=1")
        changed=readiness(self.path)
        self.assertFalse(changed['ready']);self.assertFalse(changed['evaluation_current'])
        with database(self.path) as c:c.execute("UPDATE research_vectors SET vector_json='[0]' WHERE evidence_id='review:1'")
        self.assertLess(readiness(self.path)['products'][0]['passages']['indexed'],3)

    def test_reference_provenance_and_hash_validation(self):
        self.assertEqual(ingest_references(self.path)['ingested'],3)
        self.assertEqual(len(references(self.path,'niacinamide')),1)
        with database(self.path) as c:
            c.execute("UPDATE source_documents SET content='{}' WHERE id='fda-label-order'")
        self.assertEqual(len(references(self.path)),2)
        self.assertTrue(all(not r['human_reviewed'] for r in references(self.path)))

    def test_graph_edges_are_attributed_not_causal(self):
        ingest_references(self.path)
        graph=connections(1,self.path)
        self.assertTrue(graph['paths'])
        self.assertTrue(all(e['relation'] in {'recorded_contains','discusses'} and e['evidence_id'] for e in graph['edges']))
        self.assertNotIn('product:5',{n['id'] for n in graph['nodes']})
        self.assertIsNone(connections(999,self.path))

    def test_query_cache_and_task_dimension_boundaries(self):
        calls=[]
        def transport(request,timeout):
            body=json.loads(request.data);dim=body['requests'][0]['outputDimensionality'];calls.append(1)
            return io.BytesIO(json.dumps({'embeddings':[{'values':[1.]+[0.]*(dim-1)}]}).encode())
        client=GeminiClient(self.path,transport)
        first=client.embed(['query'],task_type='RETRIEVAL_QUERY',dimensions=3)
        with run_budget(1) as run:
            second=client.embed(['query'],task_type='RETRIEVAL_QUERY',dimensions=3)
            self.assertEqual(run['calls'],0)
        self.assertEqual(first,second);self.assertTrue(client.last_telemetry['cache_hit'])
        client.embed(['query'],task_type='RETRIEVAL_DOCUMENT',dimensions=3)
        client.embed(['query'],task_type='RETRIEVAL_QUERY',dimensions=4)
        self.assertEqual(len(calls),3)

    def test_bad_query_cache_is_not_trusted(self):
        client=GeminiClient(self.path,lambda *a,**k:io.BytesIO(b'{"embeddings":[{"values":[1,0,0]}]}'))
        client.embed(['q'],task_type='RETRIEVAL_QUERY',dimensions=3)
        with database(self.path) as c:c.execute("UPDATE embedding_query_cache SET vector_json='[[0,0,0]]'")
        client.embed(['q'],task_type='RETRIEVAL_QUERY',dimensions=3)
        self.assertFalse(client.last_telemetry['cache_hit'])

    def test_explicit_plan_avoids_provider_call(self):
        from skintellect.research.model_steps import choose_plan
        with patch('skintellect.gemini.urllib.request.urlopen') as transport:
            plan,mode=choose_plan('Summarize reviews and suggest alternatives',self.path,'auto')
            transport.assert_not_called()
        self.assertEqual(plan,['reviews','alternatives','retrieve']);self.assertEqual(mode,'explicit_request_plan')

    def test_semantic_only_does_not_silently_return_lexical(self):
        from skintellect.research.retrieval import retrieve_hybrid
        result=retrieve_hybrid('ceramide',self.path,mode='semantic')
        self.assertEqual(result['mode'],'semantic_unavailable');self.assertEqual(result['documents'],[])

    def test_scoped_corpus_does_not_process_unrelated_reviews(self):
        from skintellect.research.retrieval import corpus
        from skintellect.research.review_store import extract_review
        with database(self.path) as c:c.execute("INSERT INTO reviews VALUES(3,3,'Unrelated review','','2026')")
        with patch('skintellect.research.review_store.extract_review',wraps=extract_review) as cleaner:
            docs=corpus(self.path,product_ids=[1])
        self.assertEqual(cleaner.call_count,2)
        self.assertTrue(all(d['product_id']==1 for d in docs))

    def test_label_transcription_cannot_verify_formula(self):
        from skintellect.research.labels import read_label
        image=base64.b64encode(b'\x89PNG\r\n\x1a\nfixture').decode()
        def transport(request,timeout):
            body=json.loads(request.data)
            self.assertEqual(body['contents'][0]['parts'][1]['inlineData']['data'],image)
            value={'ingredients':['Water','Panthenol'],'uncertain_text':[],'appears_complete':True}
            return io.BytesIO(json.dumps({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(value)}]}}]}).encode())
        with database(self.path) as c:before=c.execute('SELECT * FROM record_quality').fetchall()
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=transport):
            result=read_label(image,'image/png',self.path,['Water','Ceramide NP'])
        self.assertFalse(result['human_verified']);self.assertFalse(result['formula_verification_changed'])
        self.assertEqual(result['comparison']['catalog_only'],['ceramide np'])
        with database(self.path) as c:self.assertEqual(before,c.execute('SELECT * FROM record_quality').fetchall())
        with self.assertRaises(ValueError):read_label('bad','image/png',self.path)



    def test_offline_evaluation_is_explicit_about_weak_labels(self):
        from scripts.evaluate_release import evaluate
        self.prepared_fixture()
        report=evaluate(self.path,live=False)
        self.assertFalse(report['human_reviewed'])
        self.assertIn('weak',report['retrieval']['label_kind'])
        self.assertEqual(report['review_agreement']['invalid_model_source_spans'],0)
        self.assertTrue(readiness(self.path)['evaluation_current'])

    @unittest.skipIf(os.environ.get('SKINTELLECT_SKIP_HTTP') == '1', 'Sandbox loopback sockets are unavailable; run this test locally.')

    @unittest.skipIf(os.environ.get('SKINTELLECT_SKIP_HTTP') == '1', 'Sandbox loopback sockets are unavailable; run this test locally.')
    def test_new_http_routes_and_scope_validation(self):
        from skintellect.api.app import app
        ingest_references(self.path);self.prepared_fixture()
        async def check():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as c:
                self.assertEqual((await c.get('/study')).status_code,200)
                self.assertTrue((await c.get('/api/research/demo')).json()['ready'])
                self.assertEqual(len((await c.get('/api/research/references')).json()['references']),3)
                self.assertEqual((await c.get('/api/products/1/connections')).status_code,200)
                r=await c.post('/api/search',json={'product_ids':[3],'required_ingredients':['ceramides']})
                self.assertEqual([p['id'] for p in r.json()['products']],[3])
                alternative=await c.post('/api/alternatives',json={'product_id':1,
                    'constraints':{'required_ingredients':['ceramides']},'product_ids':[1,3]})
                self.assertEqual([p['id'] for p in alternative.json()['alternatives']],[3])
                self.assertEqual((await c.post('/api/assistant/query',json={'query':'q','product_ids':[]})).status_code,422)
        asyncio.run(check())

    def test_readiness_respects_configured_embedding_dimensions(self):
        self.prepared_fixture()
        with patch.dict(os.environ,{'GEMINI_EMBEDDING_DIMENSIONS':'256'}):
            self.assertFalse(readiness(self.path)['ready'])
            with database(self.path) as c:
                c.execute('UPDATE research_vectors SET dimensions=256,vector_json=?',
                    (json.dumps([1.]+[0.]*255),))
            self.assertTrue(readiness(self.path)['ready'])


if __name__=='__main__':unittest.main()
