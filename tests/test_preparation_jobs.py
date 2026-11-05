import os
"""Queue lifecycle, persistence, budgets, cancellation and fresh coverage contracts."""
import asyncio
import hashlib
import json
import unittest
from unittest.mock import PropertyMock, patch

import httpx

from skintellect.database import database
from skintellect.gemini import GeminiUnavailable
from skintellect.research import jobs
from tests import test_research as fixtures


class PreparationJobTests(unittest.TestCase):
    def setUp(self):
        fixtures.ResearchTests.setUp(self)
        jobs.initialize(self.path)
        self.enabled=patch('skintellect.gemini.GeminiClient.available',new_callable=PropertyMock,return_value=True)
        self.enabled.start()

    def tearDown(self):
        self.enabled.stop()
        fixtures.ResearchTests.tearDown(self)

    def create(self,kind='reviews'):
        return jobs.create_job(self.path,kind,10,None,2,30)

    def test_active_unique_and_persistent(self):
        jid=self.create()
        with self.assertRaisesRegex(ValueError,'already_active'):
            self.create('embed')
        jobs.initialize(self.path)
        self.assertEqual(jobs.history(self.path)[0]['id'],jid)

    def test_cancel_before_execution_and_requeue(self):
        jid=self.create()
        self.assertTrue(jobs.cancel(self.path,jid))
        with patch('skintellect.research.preparation.prepare_reviews') as prepare:
            jobs.execute(self.path,jid)
            prepare.assert_not_called()
        self.assertEqual(jobs.history(self.path)[0]['status'],'cancelled')
        self.assertFalse(jobs.cancel(self.path,jid))
        self.assertGreater(self.create(),jid)

    def test_budget_pause_keeps_saved_progress(self):
        jid=self.create()
        def prepare(*args,**kwargs):
            kwargs['on_progress'](5,10)
            raise GeminiUnavailable('run_budget_exhausted')
        with patch('skintellect.research.preparation.prepare_reviews',side_effect=prepare):
            jobs.execute(self.path,jid)
        job=jobs.history(self.path)[0]
        self.assertEqual((job['status'],job['completed'],job['selected']),('paused',5,10))
        self.create()

    def test_restart_recovery(self):
        self.create()
        jobs.recover_interrupted(self.path)
        self.assertEqual(jobs.history(self.path)[0]['status'],'interrupted')
        self.create()

    def test_pipeline_cancel_between_batches_then_resume(self):
        from skintellect.research.preparation import prepare_reviews
        with database(self.path) as c:
            c.execute("UPDATE reviews SET review_text='Gentle on my skin.' WHERE id=2")
        saved=[]
        def analyze(rows,*args):
            return {row['id']:[] for row in rows}
        with patch('skintellect.research.model_steps.analyze_review_batch',side_effect=analyze) as model:
            first=prepare_reviews(self.path,limit=2,batch_size=1,
                on_progress=lambda completed,selected:saved.append(completed),
                should_stop=lambda:bool(saved and saved[-1]>=1))
            self.assertEqual(first['processed_reviews'],1)
            second=prepare_reviews(self.path,limit=2,batch_size=1)
            self.assertEqual(second['processed_reviews'],1)
            self.assertEqual(model.call_count,2)
    def test_error_redacted(self):
        jid=self.create()
        with patch('skintellect.research.preparation.prepare_reviews',side_effect=RuntimeError('secret-key')):
            jobs.execute(self.path,jid)
        self.assertEqual(jobs.history(self.path)[0]['error_code'],'preparation_internal_error')
        self.assertNotIn('secret-key',json.dumps(jobs.history(self.path)))

    def test_completed_embedding_scope(self):
        jid=jobs.create_job(self.path,'embed',10,1,2,30)
        def index(*args,**kwargs):
            self.assertEqual(kwargs['product_ids'],[1])
            kwargs['on_progress'](2,2)
            return {'indexed':2,'pending_selected':2}
        with patch('skintellect.research.retrieval.index_embeddings',side_effect=index):
            jobs.execute(self.path,jid)
        job=jobs.history(self.path)[0]
        self.assertEqual((job['status'],job['completed']),('completed',2))

    def test_coverage_excludes_stale_duplicates_seeds(self):
        from skintellect.gemini import GeminiClient
        from skintellect.research.model_steps import REVIEW_VERSION, review_client
        client=GeminiClient(self.path)
        with database(self.path) as c:
            raw=c.execute('SELECT review_text FROM reviews WHERE id=1').fetchone()[0]
            c.execute('INSERT INTO review_aspects VALUES(?,?,?,?)',(1,hashlib.sha256(raw.encode()).hexdigest(),REVIEW_VERSION+':'+review_client(self.path).model,'[]'))
            c.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',('review:1',client.embedding_model,'old-hash',1,'[1]'))
        report=jobs.snapshot(self.path)
        self.assertEqual(report['reviews'],{'eligible':1,'processed':1,'remaining':0})
        self.assertEqual(report['embeddings']['indexed'],0)
        self.assertEqual(report['embeddings']['stale_or_out_of_scope'],1)
        self.assertEqual(report['embeddings']['eligible'],6)

    @unittest.skipIf(os.environ.get('SKINTELLECT_SKIP_HTTP') == '1', 'Sandbox loopback sockets are unavailable; run this test locally.')
    def test_http_routes_and_validation(self):
        from skintellect.api.app import app
        async def check():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as client:
                response=await client.get('/progress')
                self.assertEqual(response.status_code,200)
                self.assertIn('job-form',response.text)
                progress = await client.get('/api/research/progress')
                self.assertEqual(progress.status_code, 200)
                self.assertEqual(progress.json()['reviews']['eligible'], 1)
                invalid=await client.post('/api/research/jobs',json={'kind':'shell','limit':0})
                self.assertEqual(invalid.status_code,422)
                with patch('skintellect.research.jobs.execute'):
                    created=await client.post('/api/research/jobs',json={'kind':'reviews','limit':10})
                    self.assertEqual(created.status_code,202)
                    conflict=await client.post('/api/research/jobs',json={'kind':'embed'})
                    self.assertEqual(conflict.status_code,409)
                    jid=created.json()['job_id']
                    self.assertEqual((await client.post(f'/api/research/jobs/{jid}/cancel')).status_code,200)
        asyncio.run(check())


if __name__=='__main__':
    unittest.main()
