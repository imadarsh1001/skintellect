import skintellect.research.reviews as review_tools
import skintellect.research.search as search_tools

"""No-network Gemini contract and adversarial tests. Never require a real API key."""
import io
import json
import os
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from pydantic import BaseModel

from skintellect.config import load_environment
from skintellect.database import database
from skintellect.gemini import GeminiClient, GeminiUnavailable, ensure_tables, run_budget
from skintellect.research import service
from skintellect.research.model_steps import analyze_review_batch, select_answer_evidence
from skintellect.research.models import SearchIntent
from skintellect.research.retrieval import corpus, index_embeddings, retrieve_hybrid
from tests import test_research as fixtures


class SampleOutput(BaseModel):
    value: str


def response(value, finish='STOP'):
    return io.BytesIO(json.dumps({'candidates':[{'finishReason':finish,'content':{'parts':[{'text':json.dumps(value)}]}}],
                                 'usageMetadata':{'promptTokenCount':12,'candidatesTokenCount':8}}).encode())


class GeminiTests(unittest.TestCase):
    def setUp(self):
        fixtures.ResearchTests.setUp(self)
        self.gemini_env=patch.dict(os.environ, {'RESEARCH_LLM_ENABLED':'1','GEMINI_API_KEY':'test-key-not-real',
            'GEMINI_BACKEND':'developer',
            'GEMINI_MODEL':'gemini-test','GEMINI_EMBEDDING_MODEL':'gemini-embedding-001',
            'GEMINI_MAX_ATTEMPTS':'2','AGENT_LLM_MODE':'auto'})
        self.gemini_env.start()

    def tearDown(self):
        self.gemini_env.stop()
        fixtures.ResearchTests.tearDown(self)

    def test_header_only_auth(self):
        def transport(request,timeout):
            self.assertNotIn('test-key',request.full_url)
            self.assertEqual(request.get_header('X-goog-api-key'),'test-key-not-real')
            payload=json.loads(request.data)
            self.assertEqual(payload['generationConfig']['responseMimeType'],'application/json')
            self.assertIn('responseJsonSchema',payload['generationConfig'])
            return response({'value':'ok'})
        result=GeminiClient(self.path,transport).structured('test','extract',{},SampleOutput)
        self.assertEqual(result.value,'ok')

    def test_cache_avoids_second_api_call(self):
        calls=[]
        def transport(*args,**kwargs):
            calls.append(1)
            return response({'value':'cached'})
        client=GeminiClient(self.path,transport)
        client.structured('test','extract',{},SampleOutput)
        with run_budget(1) as run:
            client.structured('test','extract',{},SampleOutput)
        self.assertEqual(len(calls),1)
        self.assertEqual(run['calls'],0)
        self.assertTrue(client.last_telemetry['cache_hit'])

    def test_prompt_version_invalidates_cache(self):
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response({'value':'ok'})) as transport:
            client=GeminiClient(self.path)
            client.structured('test','extract',{},SampleOutput,version='1')
            client.structured('test','extract',{},SampleOutput,version='2')
            self.assertEqual(transport.call_count,2)

    def test_invalid_output_is_not_cached(self):
        client=GeminiClient(self.path,lambda *a,**k:response({'wrong':'field'}))
        with self.assertRaises(GeminiUnavailable):
            client.structured('test','extract',{},SampleOutput)
        with database(self.path) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM gemini_cache').fetchone()[0],0)

    def test_truncated_output_rejected(self):
        client=GeminiClient(self.path,lambda *a,**k:response({'value':'ok'},finish='MAX_TOKENS'))
        with self.assertRaisesRegex(GeminiUnavailable,'incomplete'):
            client.structured('test','extract',{},SampleOutput)

    def test_http_error_redacts_provider_body(self):
        def transport(*a,**k):
            raise urllib.error.HTTPError('https://example.invalid',403,'secret-test-key',{},io.BytesIO(b'secret-test-key'))
        client=GeminiClient(self.path,transport)
        with self.assertRaises(GeminiUnavailable) as error:
            client.structured('test','extract',{},SampleOutput)
        self.assertEqual(str(error.exception),'provider_http_403')
        self.assertNotIn('secret',json.dumps(client.last_telemetry))

    def test_budget_bounds_retries(self):
        def transport(*a,**k):
            raise urllib.error.HTTPError('https://example.invalid',429,'rate limit',{},io.BytesIO())
        with patch('skintellect.gemini.time.sleep'):
            with run_budget(max_calls=1) as run:
                with self.assertRaisesRegex(GeminiUnavailable,'budget'):
                    GeminiClient(self.path,transport).structured('test','extract',{},SampleOutput)
        self.assertEqual(run['calls'],1)

    def test_disabled_mode_makes_no_requests(self):
        with patch.dict(os.environ,{'RESEARCH_LLM_ENABLED':'0'}):
            with patch('skintellect.gemini.urllib.request.urlopen') as transport:
                with self.assertRaisesRegex(GeminiUnavailable,'disabled'):
                    GeminiClient(self.path).structured('test','extract',{},SampleOutput)
                transport.assert_not_called()

    def test_no_model_path_injection(self):
        with patch.dict(os.environ,{'GEMINI_MODEL':'../anything?key=bad'}):
            with self.assertRaisesRegex(GeminiUnavailable,'invalid_model'):
                GeminiClient(self.path)

    def test_intent_cannot_erase_fragrance_exclusion(self):
        intent=SearchIntent(category='moisturizers').model_dump()
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(intent)):
            result=search_tools.interpret('fragrance-free moisturizer')
        self.assertIn('Parfum',result['intent']['excluded_ingredients'])

    def test_intent_cannot_erase_exact_price_blocker(self):
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(SearchIntent(category='moisturizers').model_dump())):
            result=search_tools.interpret('moisturizer under 800 rupees')
        self.assertTrue(result['intent']['unresolved_terms'])

    def test_review_unknown_identity_rejected(self):
        payload={'observations':[{'review_id':999,'aspect':'stinging','sentiment':'positive','negated':True,'quote':"Didn't sting."}]}
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(payload)):
            with self.assertRaisesRegex(GeminiUnavailable,'evidence_validation'):
                analyze_review_batch([{'id':1,'cleaned_text':"Didn't sting."}],self.path)

    def test_invented_review_quote_rejected(self):
        payload={'observations':[{'review_id':1,'aspect':'stinging','sentiment':'positive','negated':False,'quote':'Never caused irritation'}]}
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(payload)):
            with self.assertRaisesRegex(GeminiUnavailable,'evidence_validation'):
                analyze_review_batch([{'id':1,'cleaned_text':'It stings.'}],self.path)

    def test_review_spans_derived_from_actual_source(self):
        payload={'observations':[{'review_id':1,'aspect':'stinging','sentiment':'positive','negated':True,'quote':"Didn't sting."}]}
        text="Hydrating. Didn't sting."
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(payload)):
            result=analyze_review_batch([{'id':1,'cleaned_text':text}],self.path)[1][0]
        self.assertEqual(text[result['start']:result['end']],result['span'])

    def test_answer_unknown_citation_rejected(self):
        payload={'selections':[{'evidence_id':'review:999','topic':'texture','quote':'Sticky.'}],'unanswered_topics':[]}
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(payload)):
            with self.assertRaisesRegex(GeminiUnavailable,'evidence_validation'):
                select_answer_evidence('texture',[{'evidence_id':'review:1','text':'Sticky.','kind':'reported_experience'}],self.path)

    def test_answer_never_displays_invented_quote(self):
        payload={'selections':[{'evidence_id':'review:1','topic':'texture','quote':'Clinically proven safe.'}],'unanswered_topics':[]}
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(payload)):
            with self.assertRaisesRegex(GeminiUnavailable,'evidence_validation'):
                select_answer_evidence('texture',[{'evidence_id':'review:1','text':'Sticky.','kind':'reported_experience'}],self.path)

    def test_embedding_normalization_and_payload(self):
        def transport(request,timeout):
            data=json.loads(request.data)
            self.assertEqual(data['requests'][0]['taskType'],'RETRIEVAL_QUERY')
            return io.BytesIO(json.dumps({'embeddings':[{'values':[3.,4.]}]}).encode())
        vector=GeminiClient(self.path,transport).embed(['text'],task_type='RETRIEVAL_QUERY',dimensions=2)[0]
        self.assertAlmostEqual(sum(x*x for x in vector),1)

    def test_nonfinite_embedding_rejected(self):
        transport=lambda *a,**k:io.BytesIO(b'{"embeddings":[{"values":[NaN,1]}]}')
        with self.assertRaisesRegex(GeminiUnavailable,'invalid_embedding'):
            GeminiClient(self.path,transport).embed(['text'],dimensions=2)

    def test_hybrid_retrieval_filters_to_product_scope(self):
        result=retrieve_hybrid('ceramide',self.path,product_ids=[1],use_embeddings=False)
        self.assertTrue(result['documents'])
        self.assertTrue(all(d['product_id']==1 for d in result['documents']))

    def test_empty_scope_does_not_expand_to_catalog(self):
        self.assertFalse(retrieve_hybrid('water',self.path,product_ids=[])['documents'])

    def test_index_resumes_without_reembedding_unchanged_text(self):
        with patch.object(GeminiClient,'embed',side_effect=lambda texts,**kwargs:[[1.]+[0.]*767 for t in texts]) as embed:
            one=index_embeddings(self.path,limit=50)
            two=index_embeddings(self.path,limit=50)
            self.assertGreater(one['indexed'],0)
            self.assertEqual(two['indexed'],0)
            self.assertEqual(embed.call_count,1)

    def test_stale_vector_not_used(self):
        ensure_tables(self.path)
        with database(self.path) as c:
            c.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',('product:1','gemini-embedding-001','old-hash',768,json.dumps([1.]*768)))
        with patch.object(GeminiClient,'embed') as embed:
            result=retrieve_hybrid('ceramide',self.path)
            embed.assert_not_called()
        self.assertEqual(result['semantic_coverage'],0)

    def test_pipeline_does_not_send_reviewer_identity(self):
        from skintellect.research.preparation import prepare_reviews
        def transport(request,timeout):
            text=json.loads(request.data)['contents'][0]['parts'][0]['text']
            data=json.loads(text)
            self.assertEqual(set(data['reviews'][0]),{'id','cleaned_text'})
            return response({'observations':[]})
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=transport):
            self.assertEqual(prepare_reviews(self.path)['processed_reviews'],1)

    def test_environment_values_never_executed_or_override_shell(self):
        path=Path(self.temp.name)/'config.env'
        path.write_text("GEMINI_MODEL='from-file'\nPATH=bad\nGEMINI_API_KEY=$(do-not-execute)\n")
        with patch.dict(os.environ,{'GEMINI_MODEL':'from-shell'}):
            prior=os.environ.get('PATH')
            load_environment(path)
            self.assertEqual(os.environ['GEMINI_MODEL'],'from-shell')
            self.assertEqual(os.environ['PATH'],prior)

    def test_full_workflow_keeps_constraints_and_real_quotes(self):
        intent=SearchIntent(category='moisturizers',required_ingredients=['ceramides'],excluded_ingredients=['Parfum']).model_dump()
        outputs=[intent,{'tools':['reviews','alternatives','retrieve']},
                 {'selections':[{'evidence_id':'product:1','topic':'hydration','quote':'ceramide np'}],'unanswered_topics':[]}]
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(outputs.pop(0))):
            result=service.assistant_query('moisturizer with ceramides and without fragrance')
        self.assertEqual([p['id'] for p in result['search']['products']],[1])
        self.assertEqual(result['trace']['model_calls'],3)
        self.assertEqual(result['synthesis']['selections'][0]['evidence_id'],'product:1')

    def test_invalid_tool_plan_falls_back_without_execution(self):
        from skintellect.research.model_steps import choose_plan
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response({'tools':['delete_database']})):
            plan,mode=choose_plan('find moisturizer',self.path)
        self.assertEqual(plan,['reviews','retrieve'])
        self.assertEqual(mode,'deterministic_plan_fallback')

    def test_hybrid_path_fuses_vectors_and_lexical_scores(self):
        ensure_tables(self.path)
        doc=next(d for d in corpus(self.path) if d['evidence_id']=='product:1')
        with database(self.path) as c:
            c.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',
                ('product:1','gemini-embedding-001',doc['content_hash'],768,json.dumps([1.]+[0.]*767)))
        with patch.object(GeminiClient,'embed',return_value=[[1.]+[0.]*767]):
            result=retrieve_hybrid('ceramide',self.path,product_ids=[1])
        self.assertEqual(result['mode'],'hybrid_rrf')
        self.assertEqual(result['semantic_coverage'],1)

    def test_review_pipeline_resume_uses_cached_observations(self):
        from skintellect.research.preparation import prepare_reviews
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response({'observations':[]})) as transport:
            first=prepare_reviews(self.path)
            second=prepare_reviews(self.path)
        self.assertEqual(first['processed_reviews'],1)
        self.assertEqual(second['processed_reviews'],0)
        self.assertEqual(transport.call_count,1)

    def test_vertex_configuration_and_native_schema(self):
        def transport(request,timeout):
            self.assertTrue(request.full_url.startswith('https://aiplatform.googleapis.com/v1/projects/test-project/locations/global/'))
            data=json.loads(request.data)
            self.assertIn('responseSchema',data['generationConfig'])
            self.assertNotIn('responseJsonSchema',data['generationConfig'])
            self.assertNotIn('temperature',data['generationConfig'])
            self.assertEqual(data['generationConfig']['thinkingConfig']['thinkingLevel'],'LOW')
            return response({'value':'ok'})
        with patch.dict(os.environ,{'GEMINI_BACKEND':'vertex','GOOGLE_CLOUD_PROJECT':'test-project',
                 'GEMINI_MODEL':'gemini-4-argon','GOOGLE_CLOUD_LOCATION':'global','GEMINI_THINKING_LEVEL':'LOW'}):
            self.assertEqual(GeminiClient(self.path,transport).structured('test','extract',{},SampleOutput).value,'ok')

    def test_vertex_embedding_predict_and_token_counts(self):
        def transport(request,timeout):
            self.assertTrue(request.full_url.endswith('gemini-embedding-001:predict'))
            data=json.loads(request.data)
            self.assertEqual(len(data['instances']),1)
            self.assertFalse(data['parameters']['autoTruncate'])
            return io.BytesIO(json.dumps({'predictions':[{'embeddings':{'values':[3.,4.],
                'statistics':{'truncated':False,'token_count':7}}}]}).encode())
        with patch.dict(os.environ,{'GEMINI_BACKEND':'vertex','GOOGLE_CLOUD_PROJECT':'test-project','GOOGLE_CLOUD_LOCATION':'global'}):
            client=GeminiClient(self.path,transport)
            self.assertEqual(len(client.embed(['one','two'],dimensions=2)),2)
            self.assertEqual(client.last_telemetry['input_tokens'],14)

    def test_vertex_rejects_untrusted_endpoint(self):
        with patch.dict(os.environ,{'GEMINI_BACKEND':'vertex','GOOGLE_CLOUD_PROJECT':'test-project',
                                    'API_ENDPOINT':'https://example.invalid'}):
            with self.assertRaisesRegex(GeminiUnavailable,'untrusted'):
                GeminiClient(self.path)

    def test_vertex_refuses_non_global_argon(self):
        with patch.dict(os.environ,{'GEMINI_BACKEND':'vertex','GOOGLE_CLOUD_PROJECT':'test-project',
                                    'GEMINI_MODEL':'gemini-4-argon','GOOGLE_CLOUD_LOCATION':'us-central1'}):
            with self.assertRaisesRegex(GeminiUnavailable,'requires_global'):
                GeminiClient(self.path)

    def test_embedding_preparation_respects_product_scope(self):
        with patch.object(GeminiClient,'embed',side_effect=lambda texts,**kwargs:[[1.]+[0.]*767 for t in texts]):
            result=index_embeddings(self.path,limit=50,product_ids=[1])
        self.assertEqual(result['indexed'],3)
        allowed={d['evidence_id'] for d in corpus(self.path) if d['product_id']==1}
        with database(self.path) as c:
            actual={r[0] for r in c.execute('SELECT evidence_id FROM research_vectors')}
        self.assertEqual(actual,allowed)

    def test_intent_cannot_drop_known_required_family(self):
        model=SearchIntent(category='moisturizers',unresolved_terms=['ceramides']).model_dump()
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(model)):
            parsed=search_tools.interpret('moisturizer with ceramides')['intent']
        self.assertIn('ceramides',parsed['required_ingredients'])
        self.assertNotIn('ceramides',parsed['unresolved_terms'])

    def test_research_instruction_is_separate_from_search_constraints(self):
        def transport(request,timeout):
            data=json.loads(json.loads(request.data)['contents'][0]['parts'][0]['text'])
            self.assertEqual(data['query'],'Find moisturizers with ceramides')
            return response(SearchIntent(required_ingredients=['ceramides']).model_dump())
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=transport):
            intent=search_tools.interpret('Find moisturizers with ceramides. Summarize texture evidence.')['intent']
        self.assertEqual(intent['category'],'moisturizers')
        self.assertFalse(intent['unresolved_terms'])

    def test_review_plan_gets_required_retrieval_dependency(self):
        outputs=[SearchIntent(category='moisturizers',required_ingredients=['ceramides']).model_dump(),
                 {'tools':['reviews']},{'selections':[],'unanswered_topics':[]}]
        with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response(outputs.pop(0))):
            result=service.assistant_query('moisturizer with ceramides')
        self.assertEqual(result['trace']['planned_tools'],['reviews'])
        self.assertIn('retrieve',result['trace']['tools'])
        self.assertTrue(result['evidence']['documents'])

    def test_embedding2_vertex_uses_embed_content_and_embedding_region(self):
        calls=[]
        def transport(request,timeout):
            self.assertIn('/locations/us-central1/',request.full_url)
            self.assertTrue(request.full_url.endswith('gemini-embedding-2:embedContent'))
            payload=json.loads(request.data);calls.append(payload)
            self.assertEqual(payload['embedContentConfig']['outputDimensionality'],128)
            self.assertNotIn('taskType',payload)
            self.assertNotIn('task_type',json.dumps(payload))
            self.assertEqual(len(payload['content']['parts']),1)
            return io.BytesIO(json.dumps({'embedding':{'values':[3.,4.]+[0.]*126},
                'usageMetadata':{'promptTokenCount':7}}).encode())
        with patch.dict(os.environ,{'GEMINI_BACKEND':'vertex','GOOGLE_CLOUD_PROJECT':'test-project',
                'GOOGLE_CLOUD_LOCATION':'global','GEMINI_EMBEDDING_LOCATION':'us-central1',
                'GEMINI_EMBEDDING_MODEL':'gemini-embedding-2'}):
            client=GeminiClient(self.path,transport)
            vectors=client.embed(['one','two'],dimensions=128)
            self.assertEqual(len(vectors),2)
            self.assertEqual(calls[0]['content']['parts'][0]['text'],'title: none | text: one')
            self.assertAlmostEqual(sum(x*x for x in vectors[0]),1)
            self.assertEqual(client.last_telemetry['input_tokens'],14)

    def test_embedding2_developer_query_prefix_and_cache(self):
        calls=[]
        def transport(request,timeout):
            self.assertTrue(request.full_url.endswith(':embedContent'))
            payload=json.loads(request.data);calls.append(payload)
            self.assertEqual(payload['content']['parts'][0]['text'],'task: search result | query: texture')
            self.assertEqual(payload['outputDimensionality'],128)
            self.assertNotIn('taskType',payload)
            return io.BytesIO(json.dumps({'embedding':{'values':[1.]+[0.]*127}}).encode())
        with patch.dict(os.environ,{'GEMINI_EMBEDDING_MODEL':'gemini-embedding-2'}):
            client=GeminiClient(self.path,transport)
            client.embed(['texture'],task_type='RETRIEVAL_QUERY',dimensions=128)
            client.embed(['texture'],task_type='RETRIEVAL_QUERY',dimensions=128)
            self.assertEqual(len(calls),1)
            self.assertTrue(client.last_telemetry['cache_hit'])

    def test_embedding2_rejects_truncation_and_wrong_dimensions(self):
        with patch.dict(os.environ,{'GEMINI_EMBEDDING_MODEL':'gemini-embedding-2'}):
            for body,code in [({'truncated':True,'embedding':{'values':[1.]*128}},'truncated_embedding'),
                              ({'embedding':{'values':[1.,0.]}},'invalid_embedding')]:
                transport=lambda *a,body=body,**k:io.BytesIO(json.dumps(body).encode())
                with self.assertRaisesRegex(GeminiUnavailable,code):
                    GeminiClient(self.path,transport).embed(['text'],dimensions=128)

    def test_index_rebuilds_changed_dimensions_and_preserves_old_model(self):
        docs=corpus(self.path,product_ids=[1]);doc=docs[0]
        ensure_tables(self.path)
        with database(self.path) as c:
            c.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',
                (doc['evidence_id'],'gemini-embedding-001',doc['content_hash'],768,json.dumps([1.]+[0.]*767)))
            c.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',
                (doc['evidence_id'],'gemini-embedding-2',doc['content_hash'],128,json.dumps([1.]+[0.]*127)))
        with patch.dict(os.environ,{'GEMINI_EMBEDDING_MODEL':'gemini-embedding-2','GEMINI_EMBEDDING_DIMENSIONS':'256'}):
            with patch.object(GeminiClient,'embed',side_effect=lambda texts,**kwargs:[[1.]+[0.]*255 for t in texts]):
                result=index_embeddings(self.path,limit=1,product_ids=[1])
            self.assertEqual(result['indexed'],1)
        with database(self.path) as c:
            rows=dict(c.execute('SELECT model,dimensions FROM research_vectors WHERE evidence_id=?',(doc['evidence_id'],)))
        self.assertEqual(rows,{'gemini-embedding-001':768,'gemini-embedding-2':256})

    def test_retrieval_does_not_use_old_dimensions_or_old_model(self):
        ensure_tables(self.path);doc=corpus(self.path,product_ids=[1])[0]
        with database(self.path) as c:
            for model in ['gemini-embedding-001','gemini-embedding-2']:
                c.execute('INSERT INTO research_vectors VALUES(?,?,?,?,?)',
                    (doc['evidence_id'],model,doc['content_hash'],128,json.dumps([1.]+[0.]*127)))
        with patch.dict(os.environ,{'GEMINI_EMBEDDING_MODEL':'gemini-embedding-2','GEMINI_EMBEDDING_DIMENSIONS':'256'}):
            with patch.object(GeminiClient,'embed') as embed:
                result=retrieve_hybrid('water',self.path,product_ids=[1])
                embed.assert_not_called()
            self.assertEqual(result['mode'],'lexical_bm25')

    def test_absa_model_is_independent_and_used_by_preparation(self):
        from skintellect.research.model_steps import review_client
        from skintellect.research.preparation import prepare_reviews
        with patch.dict(os.environ,{'GEMINI_ABSA_MODEL':'cheaper-review-test'}):
            self.assertEqual(GeminiClient(self.path).model,'gemini-test')
            self.assertEqual(review_client(self.path).model,'cheaper-review-test')
            with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response({'observations':[]})):
                result=prepare_reviews(self.path,limit=1)
            self.assertEqual(result['version'],'gemini-aspects-2-open:cheaper-review-test')
            insights=review_tools.review_insights(1)
            self.assertEqual(insights['gemini_reviews'],1)

    def test_absa_model_cache_is_not_reused_after_model_switch(self):
        from skintellect.research.preparation import prepare_reviews
        with patch.dict(os.environ,{'GEMINI_ABSA_MODEL':'cheaper-review-test'}):
            with patch('skintellect.gemini.urllib.request.urlopen',side_effect=lambda *a,**k:response({'observations':[]})):
                prepare_reviews(self.path,limit=1)
        with patch.dict(os.environ,{'GEMINI_ABSA_MODEL':'different-review-test'}):
            self.assertEqual(review_tools.review_insights(1)['gemini_reviews'],0)

    def test_embedding2_oauth_is_header_only_and_generation_keeps_api_key(self):
        def transport(request,timeout):
            self.assertNotIn('test-oauth-token',request.full_url)
            if request.full_url.endswith(':embedContent'):
                self.assertEqual(request.get_header('Authorization'),'Bearer test-oauth-token')
                self.assertIsNone(request.get_header('X-goog-api-key'))
                return io.BytesIO(json.dumps({'embedding':{'values':[1.]+[0.]*127}}).encode())
            self.assertEqual(request.get_header('X-goog-api-key'),'test-key-not-real')
            self.assertIsNone(request.get_header('Authorization'))
            return response({'value':'ok'})
        with patch.dict(os.environ,{'GEMINI_BACKEND':'vertex','GOOGLE_CLOUD_PROJECT':'test-project',
                'GEMINI_EMBEDDING_MODEL':'gemini-embedding-2','GEMINI_EMBEDDING_ACCESS_TOKEN':'test-oauth-token'}):
            client=GeminiClient(self.path,transport)
            client.embed(['text'],dimensions=128)
            client.structured('test','extract',{},SampleOutput)

    def test_embedding_config_update_preserves_other_settings(self):
        from skintellect.config import set_embedding_model
        target=Path(self.temp.name)/'synthetic-settings'
        target.write_text('GEMINI_API_KEY=synthetic-only\nGEMINI_EMBEDDING_MODEL=gemini-embedding-001\n',encoding='utf8')
        set_embedding_model('gemini-embedding-2',target)
        self.assertEqual(target.read_text(),'GEMINI_API_KEY=synthetic-only\nGEMINI_EMBEDDING_MODEL=gemini-embedding-2\n')


if __name__=='__main__':
    unittest.main()
