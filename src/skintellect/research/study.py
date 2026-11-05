"""Reproducible prepared cohort, resumable preparation, and live readiness checks."""
import argparse
import hashlib
import json
from datetime import datetime, timezone

from skintellect.config import DB_PATH
from skintellect.database import database, migrate
from skintellect.gemini import GeminiClient, GeminiUnavailable, ensure_tables, run_budget
from skintellect.research.passage_index import PassageIndex
from skintellect.research.review_store import ReviewCorpus

PREFERRED_IDS=[10256,21620,37102]
RELEASE_ID='prepared-research-v1'


def initialize(db_path):
    ensure_tables(db_path)
    with database(db_path) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS research_releases(
            id TEXT PRIMARY KEY,manifest_json TEXT NOT NULL,report_json TEXT,updated_at TEXT NOT NULL)''')


def select_cohort(db_path):
    from skintellect.catalog.products import load_records
    initialize(db_path)
    with database(db_path) as c:
        current=c.execute('SELECT manifest_json FROM research_releases WHERE id=?',(RELEASE_ID,)).fetchone()
        if current:
            return json.loads(current[0])
    reviews = {}
    for source in ReviewCorpus(db_path).read():
        reviews.setdefault(source['product_id'], []).append(source)
    eligible=[p for p in load_records(db_path) if p.get('is_seed')==0 and len(p['names'])>=10
              and 3<=len(reviews.get(p['id'],[]))<=20]
    eligible.sort(key=lambda p:(PREFERRED_IDS.index(p['id']) if p['id'] in PREFERRED_IDS else 100,
                                -len(reviews[p['id']]),p['id']))
    chosen=eligible[:3]
    manifest={'id':RELEASE_ID,'product_ids':[p['id'] for p in chosen],
        'selection':'Deterministic focused demo: real products with at least ten recorded ingredients and 3–20 unique reviews; preferred IDs then review coverage.',
        'products':[{'id':p['id'],'brand':p.get('brand'),'name':p['name'],'recorded_ingredients':len(p['names']),
                     'selected_reviews':len(reviews[p['id']])} for p in chosen],
        'limitations':'A small convenience sample, not representative market coverage. Formula completeness remains unverified.',
        'created_at':datetime.now(timezone.utc).isoformat()}
    with database(db_path) as c:
        c.execute('INSERT INTO research_releases VALUES(?,?,NULL,?)',
            (RELEASE_ID,json.dumps(manifest),datetime.now(timezone.utc).isoformat()))
    return manifest


def readiness(db_path):
    from skintellect.catalog.products import load_records
    from skintellect.research.model_steps import REVIEW_VERSION, review_client
    from skintellect.research.retrieval import corpus
    initialize(db_path)
    with database(db_path) as c:
        row=c.execute('SELECT manifest_json,report_json FROM research_releases WHERE id=?',(RELEASE_ID,)).fetchone()
        if not row:
            return {'configured':False,'ready':False,'products':[],'product_ids':[],'evaluation':None}
        manifest=json.loads(row[0]);evaluation=json.loads(row[1]) if row[1] else None
    client=GeminiClient(db_path)
    ids=manifest['product_ids']
    docs=corpus(db_path,product_ids=ids)
    current={p['id']:p for p in load_records(db_path) if p.get('is_seed')==0}
    products=[]
    with database(db_path) as c:
        review_store = ReviewCorpus(db_path)
        review_sources = review_store.read(product_ids=ids)
        prepared_reviews = review_store.cached(review_client(db_path).model, review_sources)
        cached = prepared_reviews.observations
        review_fingerprint = prepared_reviews.fingerprints
        passage_state = PassageIndex(db_path, client.embedding_model, client.embedding_dimensions).read(docs)
        vector_fingerprint = passage_state.fingerprints
        for selected in manifest['products']:
            pid = selected['id']
            sources = [r for r in review_sources if r['product_id'] == pid]
            eligible = len(sources)
            processed = sum(r['id'] in cached for r in sources)
            scoped=[d for d in docs if d['product_id']==pid]
            indexed=sum(d['evidence_id'] in passage_state.vectors for d in scoped)
            p=current.get(pid)
            products.append(selected|{'available':p is not None,'name':p['name'] if p else selected['name'],
                'reviews':{'eligible':eligible,'processed':processed},'passages':{'eligible':len(scoped),'indexed':indexed},
                'ready':bool(p and p['names'] and eligible and eligible==processed and scoped and indexed==len(scoped))})
    from skintellect.research.references import references
    absa_model=review_client(db_path).model
    model_identity=client.model if absa_model==client.model else {'generation':client.model,'absa':absa_model}
    fingerprint=hashlib.sha256(json.dumps([model_identity,client.embedding_model,REVIEW_VERSION,
        sorted((d['evidence_id'],d['content_hash']) for d in docs),review_fingerprint,
        sorted(vector_fingerprint),[(r['evidence_id'],r['content_hash']) for r in references(db_path)]],sort_keys=True).encode()).hexdigest()
    return manifest|{'configured':True,'ready':bool(products) and all(p['ready'] for p in products),
        'products':products,'evaluation':evaluation,'input_fingerprint':fingerprint,
        'evaluation_current':bool(evaluation and evaluation.get('input_fingerprint')==fingerprint),
        'example_query':'Find moisturizers with ceramides. Summarize texture evidence and suggest one alternative.'}


def prepare_cohort(db_path,max_calls=80,max_seconds=1800):
    from skintellect.research.preparation import prepare_reviews
    from skintellect.research.retrieval import index_embeddings
    manifest=select_cohort(db_path)
    if not manifest['product_ids']:
        raise ValueError('no_eligible_cohort_products')
    events=[]
    with run_budget(max_calls,max_seconds) as run:
        try:
            for pid in manifest['product_ids']:
                prepare_reviews(db_path,limit=5000,product_id=pid)
            index_embeddings(db_path,limit=5000,product_ids=manifest['product_ids'])
        except GeminiUnavailable as exc:
            events.append({'error_code':str(exc)})
        result=readiness(db_path)
        return {'cohort':result,'calls':run['calls'],'events':run['events'],'errors':events}


def save_evaluation(db_path,report):
    initialize(db_path)
    with database(db_path) as c:
        c.execute('UPDATE research_releases SET report_json=?,updated_at=? WHERE id=?',
            (json.dumps(report),datetime.now(timezone.utc).isoformat(),RELEASE_ID))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['select','prepare','status'])
    parser.add_argument('--max-calls',type=int,default=80)
    parser.add_argument('--max-seconds',type=int,default=1800)
    parser.add_argument('--output')
    args=parser.parse_args()
    if not 1<=args.max_calls<=1000 or not 10<=args.max_seconds<=3600:parser.error('Invalid budget')
    migrate(DB_PATH)
    result=select_cohort(DB_PATH) if args.command=='select' else (prepare_cohort(DB_PATH,args.max_calls,args.max_seconds) if args.command=='prepare' else readiness(DB_PATH))
    value=json.dumps(result,indent=2)
    if args.output:
        from pathlib import Path
        output=Path(args.output)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(value,encoding='utf-8')
    print(value)
    return 2 if args.command=='prepare' and not result['cohort']['ready'] else 0


if __name__=='__main__':raise SystemExit(main())
