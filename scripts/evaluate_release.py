"""Automated release checks, weak-label retrieval comparisons and measured latency.

This is reproducible engineering evaluation. Model agreement and generated relevance
labels are explicitly NOT independent human ground truth or real-world accuracy.
"""
import argparse
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.evaluate_review_nlp import CASES, metrics
from skintellect.config import DB_PATH
from skintellect.database import database
from skintellect.gemini import GeminiClient, run_budget
from skintellect.research.model_steps import REVIEW_VERSION, review_client
from skintellect.research.retrieval import corpus, lexical, retrieve_hybrid
from skintellect.research.review_store import extract_review
from skintellect.research.study import readiness, save_evaluation


def ranking_metrics(ranking,relevant,k=3):
    found=[eid for eid in ranking[:k] if eid in relevant]
    rr=next((1/(i+1) for i,eid in enumerate(ranking) if eid in relevant),0)
    dcg=sum(1/math.log2(i+2) for i,eid in enumerate(ranking[:k]) if eid in relevant)
    ideal=sum(1/math.log2(i+2) for i in range(min(k,len(relevant))))
    return {'mrr':rr,'precision_at_3':len(found)/k,'recall_at_3':len(found)/len(relevant) if relevant else 0,
            'ndcg_at_3':dcg/ideal if ideal else 0}


def review_agreement(db_path,ids):
    client=GeminiClient(db_path);details=[];invalid=0
    with database(db_path) as c:
        for rid,pid,raw in c.execute('SELECT id,product_id,review_text FROM reviews ORDER BY id'):
            if pid not in ids:continue
            h=hashlib.sha256((raw or '').encode()).hexdigest()
            stored=c.execute('SELECT observations_json FROM review_aspects WHERE review_id=? AND input_hash=? AND extraction_version=?',
                (rid,h,REVIEW_VERSION+':'+review_client(db_path).model)).fetchone()
            if not stored:continue
            clean,rules=extract_review(raw);model=json.loads(stored[0])
            invalid+=sum(clean[o['start']:o['end']]!=o['span'] for o in model)
            a={(o['aspect'],o['sentiment'],o['negated']) for o in rules}
            b={(o['aspect'],o['sentiment'],o['negated']) for o in model}
            details.append({'review_id':rid,'product_id':pid,'exact_label_set_agreement':a==b,
                'jaccard_agreement':len(a&b)/len(a|b) if a|b else 1,
                'rules_only':[list(x) for x in sorted(a-b)],'gemini_only':[list(x) for x in sorted(b-a)]})
    return {'kind':'real_review_rules_model_agreement_not_accuracy','reviews':len(details),
        'exact_set_agreement':sum(d['exact_label_set_agreement'] for d in details)/len(details) if details else None,
        'mean_jaccard_agreement':sum(d['jaccard_agreement'] for d in details)/len(details) if details else None,
        'invalid_model_source_spans':invalid,'disagreements':[d for d in details if not d['exact_label_set_agreement']],
        'limitation':'Both methods can be wrong. No independent human annotations were supplied.'}


def evaluate(db_path,live=True):
    from skintellect.research import service
    from skintellect.research.references import source_passages
    status=readiness(db_path);ids=status['product_ids']
    if not status['ready']:raise ValueError('prepare_cohort_before_evaluation')
    docs=corpus(db_path,product_ids=ids)
    cases=[{'query':p['brand']+' '+p['name'],'relevant':['product:'+str(p['id'])],
            'label_basis':'known_catalog_identity'} for p in status['products']]
    for term in ('niacinamide','ceramide','glycerin','sticky','hydrating'):
        relevant=[d['evidence_id'] for d in docs if term in d['text'].casefold()]
        if relevant:cases.append({'query':term,'relevant':relevant,'label_basis':'surface_term_match_weak_label'})
    results=[];latencies=[]
    with run_budget(30,900) as run:
        for case in cases:
            row=case|{'rankings':{}}
            for mode in (['lexical','semantic','hybrid'] if live else ['lexical']):
                start=time.perf_counter()
                r=retrieve_hybrid(case['query'],db_path,ids,limit=10,use_embeddings=live,mode=mode)
                elapsed=round((time.perf_counter()-start)*1000,2)
                ranking=[d['evidence_id'] for d in r['documents']]
                row['rankings'][mode]={'metrics':ranking_metrics(ranking,set(case['relevant'])),
                    'evidence_ids':ranking,'elapsed_ms':elapsed,'actual_mode':r['mode'],'semantic_status':r['semantic_status']}
            results.append(row)
        if live:
            query=status['example_query']
            for label in ['first_run_in_this_benchmark','repeat_run']:
                answer=service.assistant_query(query,ids,planning_mode='auto',db_path=db_path)
                bundle={d['evidence_id']:d['text'] for d in answer['evidence']['documents']}
                supported=all(s['evidence_id'] in bundle and s['quote'] in bundle[s['evidence_id']] for s in answer['synthesis']['selections'])
                latencies.append({'run':label,'elapsed_ms':answer['trace']['elapsed_ms'],
                    'provider_calls':answer['trace']['model_calls'],'cache_hits':answer['trace']['cache_hits'],
                    'stage_timings_ms':answer['trace']['stage_timings_ms'],
                    'evidence_selection_mode':answer['synthesis']['mode'],
                    'selected_quotes':len(answer['synthesis']['selections']),'all_selected_quotes_supported':supported})
        usage={'provider_calls':run['calls']+sum(r['provider_calls'] for r in latencies),
               'retrieval_provider_calls':run['calls'],'retrieval_events':run['events']}
    summaries={}
    for mode in (['lexical','semantic','hybrid'] if live else ['lexical']):
        summaries[mode]={key:sum(r['rankings'][mode]['metrics'][key] for r in results)/len(results)
                         for key in ['mrr','precision_at_3','recall_at_3','ndcg_at_3']} if results else {}
    synthetic=metrics(CASES,{c['id']:extract_review(c['text'])[1] for c in CASES})
    refs=source_passages(db_path)
    report={'created_at':datetime.now(timezone.utc).isoformat(),'input_fingerprint':status['input_fingerprint'],
        'evaluation_kind':'automated_engineering_checks_not_human_validated_accuracy',
        'cohort_product_ids':ids,'cohort_ready':status['ready'],
        'retrieval':{'label_kind':'generated_identity_and_surface_term_weak_labels','cases':results,'summary':summaries,
            'limitation':'Small convenience sample. Surface labels favor lexical matching. These scores do not establish semantic relevance or ranking gains.'},
        'review_agreement':review_agreement(db_path,ids),
        'synthetic_rule_smoke':{'kind':'authored_synthetic_developer_fixtures','cases':len(CASES),'metrics':synthetic},
        'latency':{'measurements':latencies,'limitation':'Two measurements; first may already have cached model steps. No production SLA claim.'},
        'reference_library':{'notes':len(refs),'lexical_smoke':dict(lexical(refs,'niacinamide ingredient fragrance'))},
        'usage':usage,'human_reviewed':False,
        'remaining_limitations':['No human gold labels','No catalog formula certified complete','No clinical product validation','Full catalog preparation is partial']}
    save_evaluation(db_path,report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline',action='store_true')
    parser.add_argument('--output',default='reports/latest/research_release_evaluation.json')
    args=parser.parse_args()
    report=evaluate(DB_PATH,not args.offline)
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'report':args.output,'review_agreement':report['review_agreement'],
        'retrieval_summary':report['retrieval']['summary'],'latency':report['latency']},indent=2))


if __name__=='__main__':main()
