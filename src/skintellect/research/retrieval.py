from skintellect.catalog.store import get_catalog

"""Lexical BM25 + Gemini vectors, fused by reciprocal ranks with source-hash checks."""
import hashlib
import re
import sqlite3
from collections import Counter

from skintellect.catalog.products import load_records
from skintellect.database import database
from skintellect.gemini import GeminiClient, GeminiUnavailable, ensure_tables
from skintellect.research.passage_index import PassageIndex
from skintellect.research.review_store import ReviewCorpus, extract_review


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def corpus(db_path,records=None,product_ids=None):
    from skintellect.catalog.products import load_records
    if product_ids is not None and not product_ids:
        return []
    docs=[]
    for p in (records if records is not None else load_records(db_path)):
        if p.get('is_seed') != 0 or (product_ids is not None and p['id'] not in product_ids):
            continue
        text=' '.join([p.get('brand') or '',p.get('name') or '',p.get('category') or '',
                       p.get('description') or '',', '.join(p['names'])])
        docs.append({'evidence_id':'product:'+str(p['id']),'product_id':p['id'],
                     'text':text,'kind':'catalog_record','content_hash':digest(text)})
    for source in ReviewCorpus(db_path).read(product_ids=product_ids, unique=False):
        cleaned = source['cleaned_text']
        if cleaned:
            docs.append({'evidence_id': 'review:' + str(source['id']), 'product_id': source['product_id'],
                         'text': cleaned, 'kind': 'reported_experience', 'content_hash': digest(cleaned)})
    return docs


def lexical(documents, query):
    tokens=re.findall(r'\w+',query.casefold())[:40]
    if not tokens or not documents:
        return []
    # The temporary index always reflects current source text; stale retrieval is impossible.
    c=sqlite3.connect(':memory:')
    try:
        c.execute("CREATE VIRTUAL TABLE passages USING fts5(evidence_id UNINDEXED, text, tokenize='porter unicode61')")
        c.executemany('INSERT INTO passages VALUES(?,?)',[(d['evidence_id'],d['text']) for d in documents])
        expression=' OR '.join('"'+t.replace('"','""')+'"' for t in tokens)
        ranks=c.execute('SELECT evidence_id,bm25(passages) FROM passages WHERE passages MATCH ? ORDER BY bm25(passages),evidence_id', (expression,)).fetchall()
        return [(eid,-score) for eid,score in ranks]
    except sqlite3.OperationalError:
        # Some SQLite builds omit FTS5; label the fallback rather than requiring a new server.
        scores=[]
        for d in documents:
            counts=Counter(re.findall(r'\w+',d['text'].casefold()))
            score=sum(counts[t]/(counts[t]+1.2) for t in tokens if counts[t])
            if score:
                scores.append((d['evidence_id'],score))
        return sorted(scores,key=lambda v:(-v[1],v[0]))
    finally:
        c.close()


def index_embeddings(db_path, limit=20, batch_size=10, kinds=None, product_ids=None, on_progress=None, should_stop=None, evidence_ids=None):
    client=GeminiClient(db_path)
    if client.backend=='vertex' or client.embedding_model=='gemini-embedding-2':
        batch_size=1  # Persist each Cloud predict result before consuming another request budget.
    ensure_tables(db_path)
    docs=corpus(db_path,product_ids=product_ids)
    if evidence_ids is not None:
        selected=set(evidence_ids)
        docs=[d for d in docs if d['evidence_id'] in selected]
    if kinds:
        docs=[d for d in docs if d['kind'] in kinds]
    index = PassageIndex(db_path, client.embedding_model, client.embedding_dimensions)
    pending = index.read(docs).pending[:limit]
    done=0
    if on_progress:
        on_progress(0,len(pending))
    for start in range(0,len(pending),batch_size):
        if should_stop and should_stop():
            break
        batch=pending[start:start+batch_size]
        vectors=client.embed([d['text'] for d in batch])
        index.save(batch, vectors)
        done+=len(batch)
        if on_progress:
            on_progress(done,len(pending))
    return {'indexed':done,'pending_selected':len(pending),'model':client.embedding_model,
            'eligible_documents':len(docs)}


def retrieve_hybrid(query, db_path, product_ids=None, limit=8, use_embeddings=True, mode='hybrid',records=None):
    if mode not in {'hybrid','lexical','semantic'}:
        raise ValueError('invalid_retrieval_mode')
    use_embeddings=use_embeddings and mode!='lexical'
    if product_ids is not None and not product_ids:
        return {'mode':'empty_product_scope','documents':[],'semantic_coverage':0}
    docs=corpus(db_path,records,product_ids)
    by_id={d['evidence_id']:d for d in docs}
    lexical_ranks=lexical(docs,query)
    client=GeminiClient(db_path)
    semantic_ranks=[]
    status='not_requested'
    if use_embeddings:
        status='not_configured_or_disabled' if not client.available else 'index_empty_or_stale'
        state = PassageIndex(db_path, client.embedding_model, client.embedding_dimensions).read(docs)
        if state.vectors and client.available:
            try:
                query_vector = client.embed([query], task_type='RETRIEVAL_QUERY')[0]
                for eid, vector in state.vectors.items():
                    if len(vector) == len(query_vector):
                        semantic_ranks.append((eid, sum(a*b for a,b in zip(vector, query_vector))))
                semantic_ranks.sort(key=lambda v: (-v[1], v[0]))
                status = 'available'
            except (GeminiUnavailable, ValueError, TypeError):
                status = 'unavailable_fallback_to_lexical'
    scores={}
    rankings=(semantic_ranks,) if mode=='semantic' else (lexical_ranks,semantic_ranks)
    for ranking in rankings:
        for rank,(eid,_) in enumerate(ranking[:100],1):
            scores[eid]=scores.get(eid,0)+1/(60+rank)
    ordered=sorted(scores,key=lambda eid:(-scores[eid],eid))[:limit]
    return {'mode':('semantic_only' if semantic_ranks else 'semantic_unavailable') if mode=='semantic' else ('hybrid_rrf' if semantic_ranks else 'lexical_bm25'),
            'documents':[by_id[eid] | {'score':round(scores[eid],6)} for eid in ordered],
            'semantic_status':status,'semantic_coverage':len(semantic_ranks),
            'scoped_documents':len(docs)}



def retrieve(query, product_ids=None, limit=8):
    db_path = get_catalog().path
    """Lexical baseline over facts and visible review spans, using stable evidence IDs."""
    tokens = set(re.findall(r'\w+', query.casefold()))
    documents = []
    for p in load_records():
        if p.get('is_seed') != 0 or (product_ids and p['id'] not in product_ids):
            continue
        text = ' '.join([p.get('name') or '', p.get('description') or '', ', '.join(p['names'])])
        documents.append({'evidence_id': 'product:' + str(p['id']), 'text': text, 'kind': 'catalog_record'})
    with database(db_path) as c:
        for rid, pid, text in c.execute('SELECT r.id,r.product_id,r.review_text FROM reviews r JOIN record_quality q ON r.product_id=q.product_id WHERE q.is_seed=0'):
            if not product_ids or pid in product_ids:
                documents.append({'evidence_id': 'review:' + str(rid), 'text': extract_review(text)[0], 'kind': 'reported_experience'})
    for d in documents:
        terms = re.findall(r'\w+', d['text'].casefold())
        counts = Counter(terms)
        d['score'] = sum(counts[t]/(counts[t]+1.2) for t in tokens if counts[t])
    documents = [d for d in documents if d['score'] > 0]
    documents.sort(key=lambda d: (-d['score'], d['evidence_id']))
    return {'mode': 'lexical_baseline', 'documents': documents[:limit]}
