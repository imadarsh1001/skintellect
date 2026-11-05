"""Durable single-worker preparation queue for the local research workspace.

Jobs have explicit request/time limits. Cancellation is cooperative between batches;
already persisted extraction results and embeddings are retained for a new job.
"""
import sqlite3
import threading
from datetime import datetime, timezone

from skintellect.database import database
from skintellect.gemini import GeminiClient, GeminiUnavailable, ensure_tables, run_budget
from skintellect.research.passage_index import PassageIndex
from skintellect.research.review_store import ReviewCorpus

_worker_lock = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat()


def initialize(db_path):
    ensure_tables(db_path)
    with database(db_path) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS preparation_jobs(
            id INTEGER PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL,
            limit_count INTEGER, product_id INTEGER, max_calls INTEGER, max_seconds INTEGER,
            completed INTEGER DEFAULT 0, selected INTEGER, calls INTEGER DEFAULT 0,
            tokens INTEGER DEFAULT 0, cancel_requested INTEGER DEFAULT 0,
            error_code TEXT, created_at TEXT, started_at TEXT, finished_at TEXT)''')
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_active_preparation_job ON preparation_jobs((1)) WHERE status IN ('queued','running')")


def recover_interrupted(db_path):
    """Called once at app startup, before accepting new jobs; use one server worker."""
    initialize(db_path)
    with database(db_path) as c:
        c.execute("UPDATE preparation_jobs SET status='interrupted',error_code='server_restarted',finished_at=? WHERE status IN ('queued','running')", (now(),))


def history(db_path):
    initialize(db_path)
    with database(db_path) as c:
        c.row_factory = sqlite3.Row
        return [dict(row) for row in c.execute('SELECT * FROM preparation_jobs ORDER BY id DESC LIMIT 30')]


def create_job(db_path, kind, limit, product_id, max_calls, max_seconds):
    initialize(db_path)
    if kind not in {'reviews','embed'} or not 1 <= limit <= 5000 or not 1 <= max_calls <= 1000 or not 10 <= max_seconds <= 3600:
        raise ValueError('invalid_job_parameters')
    if not GeminiClient(db_path).available:
        raise GeminiUnavailable('disabled_or_missing_key')
    with database(db_path) as c:
        if product_id is not None and not c.execute('SELECT 1 FROM record_quality WHERE product_id=? AND is_seed=0',(product_id,)).fetchone():
            raise ValueError('nonseed_product_not_found')
        try:
            cursor = c.execute('''INSERT INTO preparation_jobs(kind,status,limit_count,product_id,max_calls,max_seconds,created_at)
                VALUES(?,'queued',?,?,?,?,?)''',(kind,limit,product_id,max_calls,max_seconds,now()))
        except sqlite3.IntegrityError:
            raise ValueError('preparation_already_active') from None
        return cursor.lastrowid


def cancel(db_path, job_id):
    with database(db_path) as c:
        changed=c.execute("UPDATE preparation_jobs SET cancel_requested=1 WHERE id=? AND status IN ('queued','running')",(job_id,)).rowcount
    return bool(changed)


def execute(db_path, job_id):
    # A second worker cannot start while the local worker owns the lock.
    with _worker_lock:
        with database(db_path) as c:
            c.row_factory=sqlite3.Row
            row=c.execute("SELECT * FROM preparation_jobs WHERE id=? AND status='queued'",(job_id,)).fetchone()
            if row is None:
                return
            job=dict(row)
            c.execute("UPDATE preparation_jobs SET status='running',started_at=? WHERE id=?",(now(),job_id))
        def stopped():
            with database(db_path) as c:
                return bool(c.execute('SELECT cancel_requested FROM preparation_jobs WHERE id=?',(job_id,)).fetchone()[0])
        def progress(completed, selected):
            tokens=sum(e.get('total_tokens') or (e.get('input_tokens',0)+e.get('output_tokens',0)+e.get('thinking_tokens',0)) for e in run['events'] if not e.get('cache_hit'))
            with database(db_path) as c:
                c.execute('UPDATE preparation_jobs SET completed=?,selected=?,calls=?,tokens=? WHERE id=?',
                          (completed,selected,run['calls'],tokens,job_id))
        state='completed'
        code=None
        with run_budget(job['max_calls'],job['max_seconds']) as run:
            try:
                if stopped():
                    state='cancelled'
                elif job['kind']=='reviews':
                    from skintellect.research.preparation import prepare_reviews
                    result=prepare_reviews(db_path,job['limit_count'],job['product_id'],on_progress=progress,should_stop=stopped)
                    progress(result['processed_reviews'],result['selected_reviews'])
                else:
                    from skintellect.research.retrieval import index_embeddings
                    result=index_embeddings(db_path,limit=job['limit_count'],
                        product_ids=[job['product_id']] if job['product_id'] is not None else None,
                        on_progress=progress,should_stop=stopped)
                    progress(result['indexed'],result['pending_selected'])
                if stopped():
                    state='cancelled'
            except GeminiUnavailable as exc:
                code=str(exc)
                state='paused' if code=='run_budget_exhausted' else 'failed'
            except Exception:
                # Provider bodies, credentials and raw exceptions never reach the UI.
                state,code='failed','preparation_internal_error'
            finally:
                with database(db_path) as c:
                    counts=c.execute('SELECT completed,selected FROM preparation_jobs WHERE id=?',(job_id,)).fetchone()
                progress(*counts)
                with database(db_path) as c:
                    c.execute('UPDATE preparation_jobs SET status=?,error_code=?,finished_at=? WHERE id=?',(state,code,now(),job_id))


def snapshot(db_path):
    """Count fresh, model/version-matching work, rather than all historical rows."""
    from skintellect.research.model_steps import review_client
    from skintellect.research.retrieval import corpus
    initialize(db_path)
    client=GeminiClient(db_path)
    docs=corpus(db_path)
    passage_state = PassageIndex(db_path, client.embedding_model, client.embedding_dimensions).read(docs)
    indexed = len(passage_state.vectors)
    review_store = ReviewCorpus(db_path)
    sources = review_store.read()
    eligible = len(sources)
    processed = len(review_store.cached(review_client(db_path).model, sources).observations)
    with database(db_path) as c:
        usage=c.execute('''SELECT COUNT(*),COALESCE(SUM(attempts),0),COALESCE(SUM(CASE WHEN cache_hit=0 THEN
            COALESCE(total_tokens,input_tokens+output_tokens+COALESCE(thinking_tokens,0)) ELSE 0 END),0),
            COALESCE(SUM(cache_hit),0) FROM gemini_runs''').fetchone()
        recent=[dict(zip(('task','status','attempts','elapsed_ms','error_code','created_at'),r)) for r in c.execute(
            'SELECT task,status,attempts,elapsed_ms,error_code,created_at FROM gemini_runs ORDER BY id DESC LIMIT 10')]
    return {'model':client.status(),'reviews':{'processed':processed,'eligible':eligible,'remaining':eligible-processed},
            'embeddings':{'indexed':indexed,'eligible':len(docs),'remaining':len(docs)-indexed,'stale_or_out_of_scope':passage_state.stored_count-indexed},
            'usage':dict(zip(('operations','provider_attempts','reported_tokens','cache_hits'),usage)),
            'jobs':history(db_path),'recent_operations':recent,'estimated_cost':None,
            'notice':'Coverage excludes seeds; reviews exclude duplicate and empty text. Tokens are provider-reported, not a billing estimate. Jobs run while this server is open.'}
