from skintellect.catalog.store import get_catalog

"""Bounded assistant workflow; lower-level modules do not depend on this module."""
import os
import time

from skintellect.catalog.products import load_records
from skintellect.research.alternatives import alternatives
from skintellect.research.evidence import RULE_VERSION
from skintellect.research.models import SearchIntent
from skintellect.research.reviews import review_insights
from skintellect.research.search import interpret, structured_search


def assistant_query(query, product_ids=None, planning_mode='auto', db_path=None):
    from skintellect.gemini import GeminiUnavailable, run_budget
    from skintellect.research.model_steps import choose_plan, select_answer_evidence
    from skintellect.research.retrieval import retrieve_hybrid
    db_path = get_catalog(db_path).path
    started = time.perf_counter()
    timings={}
    def measured(name, action):
        start=time.perf_counter()
        try:return action()
        finally:timings[name]=round((time.perf_counter()-start)*1000,2)
    with run_budget(max_calls=6, max_seconds=120) as run:
        parsed = measured('interpret',lambda:interpret(query, db_path))
        intent = SearchIntent(**parsed['intent'])
        records=measured('load_catalog',lambda:load_records(db_path))
        result = measured('search',lambda:structured_search(intent,product_ids,records))
        result['product_scope']=product_ids
        ids = [p['id'] for p in result['products'][:3]]
        plan, plan_mode = measured('plan',lambda:choose_plan(query, db_path,planning_mode)) if ids else ([], 'no_eligible_candidates')
        planned_tools=list(plan)
        # Review summaries require source passages even if the model omits that dependency.
        if 'reviews' in plan and 'retrieve' not in plan:
            plan.append('retrieve')
        reviews = measured('reviews',lambda:[review_insights(pid, db_path) for pid in ids]) if 'reviews' in plan else []
        similar = measured('alternatives',lambda:[alternatives(pid, intent,records,product_ids) for pid in ids[:1]]) if 'alternatives' in plan else []
        bundle = measured('retrieve',lambda:retrieve_hybrid(query, db_path, ids, use_embeddings=os.environ.get('RESEARCH_HYBRID_ENABLED','1')=='1',records=records)) if ids and 'retrieve' in plan else {'mode':'not_requested','documents':[]}
        # Only currently eligible product IDs enter recommendations. Gemini can select exact excerpts.
        try:
            synthesis = measured('evidence_selection',lambda:select_answer_evidence(query, bundle['documents'], db_path))
        except GeminiUnavailable as exc:
            synthesis = {'mode':'evidence_selection_fallback','selections':[],'unanswered_topics':[],
                         'error_code':str(exc)}
        answer = ('Please resolve the highlighted constraints.' if result['needs_clarification'] else
                  f"Found {result['total']} eligible catalog records; {result['unknown_count']} have unknown ingredient constraints.")
        from skintellect.research.references import references
        return {'answer':answer, 'search':result, 'review_insights':reviews, 'alternatives':similar,
                'references':references(db_path,query),
                'evidence':bundle, 'synthesis':synthesis,
                'trace':{'mode':'gemini_research_workflow' if run['calls'] else 'deterministic_workflow',
                    'rule_version':RULE_VERSION, 'tools':['interpret','structured_search']+plan+['validate_evidence'],
                    'plan_mode':plan_mode, 'planned_tools':planned_tools,
                    'events':run['events'], 'retries':sum(max(0,e['attempts']-1) for e in run['events']),
                    'model_calls':run['calls'], 'interpretation_mode':parsed['mode'],
                    'stage_timings_ms':timings,
                    'cache_hits':sum(bool(e.get('cache_hit')) for e in run['events']),
                    'input_tokens':sum(e['input_tokens'] for e in run['events']),
                    'output_tokens':sum(e['output_tokens'] for e in run['events']),
                    'thinking_tokens':sum(e.get('thinking_tokens',0) for e in run['events']),
                    'elapsed_ms':round((time.perf_counter()-started)*1000,2)}}
