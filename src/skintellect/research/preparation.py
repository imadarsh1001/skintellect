from skintellect.catalog.store import get_catalog

"""Resumable, budgeted Gemini review extraction and embedding preparation.

Run python -m skintellect.research.preparation status / reviews / embed / smoke.
API credentials are read from local .env, never accepted as command-line arguments.
"""
import argparse
import json

from skintellect.config import DB_PATH
from skintellect.database import migrate
from skintellect.gemini import GeminiClient, GeminiUnavailable, ensure_tables, run_budget
from skintellect.research.review_store import ReviewCorpus


def prepare_reviews(db_path=None, limit=20, product_id=None, batch_size=5, on_progress=None, should_stop=None, review_ids=None):
    from skintellect.research.model_steps import analyze_review_batch, review_client
    db_path = get_catalog(db_path).path
    client=review_client(db_path)
    store = ReviewCorpus(db_path)
    sources = store.read(product_ids=[product_id] if product_id is not None else None,
                         review_ids=review_ids)
    cached = store.cached(client.model, sources).observations
    pending = [r for r in sources if r['id'] not in cached][:limit]
    processed=0
    if on_progress:
        on_progress(0,len(pending))
    for offset in range(0,len(pending),batch_size):
        if should_stop and should_stop():
            break
        batch=pending[offset:offset+batch_size]
        extracted=analyze_review_batch([{'id':r['id'],'cleaned_text':r['cleaned_text']} for r in batch],db_path,client)
        store.save(client.model, batch, extracted)
        processed+=len(batch)
        if on_progress:
            on_progress(processed,len(pending))
    return {'processed_reviews':processed,'selected_reviews':len(pending),'version':store.version(client.model)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['status','reviews','embed','smoke'])
    parser.add_argument('--limit',type=int,default=20)
    parser.add_argument('--product-id',type=int)
    parser.add_argument('--max-calls',type=int,default=8)
    args=parser.parse_args()
    if not 1<=args.limit<=5000 or not 1<=args.max_calls<=1000:
        parser.error('limit must be 1..5000 and max-calls 1..1000')
    migrate()
    ensure_tables(DB_PATH)
    client=GeminiClient(DB_PATH)
    try:
        with run_budget(args.max_calls,max_seconds=120) as run:
            if args.command=='status':
                result=client.status()
            elif args.command=='reviews':
                result=prepare_reviews(limit=args.limit,product_id=args.product_id)
            elif args.command=='embed':
                from skintellect.research.retrieval import index_embeddings
                result=index_embeddings(DB_PATH,limit=args.limit,
                    product_ids=[args.product_id] if args.product_id is not None else None)
            else:
                from skintellect.research.models import ReviewExtraction
                result=client.structured('connection_smoke','Extract only literal supported review observations.',
                    {'review_id':1,'text':"Hydrating but sticky. Didn't sting."},ReviewExtraction,'1',1500).model_dump()
            print(json.dumps({'result':result,'usage':run},indent=2))
    except GeminiUnavailable as exc:
        print(json.dumps({'status':'unavailable','error_code':str(exc),'configured':bool(client.api_key)}))
        raise SystemExit(2)


if __name__=='__main__':
    main()
