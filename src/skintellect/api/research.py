import skintellect.catalog.products as products
import skintellect.research.alternatives as alternative_tools
import skintellect.research.evidence as evidence_tools
import skintellect.research.reviews as review_tools
import skintellect.research.search as search_tools

"""Typed, bounded endpoints for the evidence-backed research release."""
from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from skintellect.catalog.store import get_catalog
from skintellect.database import audit
from skintellect.gemini import GeminiClient, GeminiUnavailable, ensure_tables, run_budget
from skintellect.research import service
from skintellect.research.models import (
    AlternativeRequest,
    ExtractionRequest,
    QueryRequest,
    SearchIntent,
    StrictModel,
)

router = APIRouter(prefix='/api', tags=['Evidence research'])


class AssistantRequest(StrictModel):
    query: str = Field(min_length=1, max_length=2000)
    product_ids: list[Annotated[int, Field(ge=1)]] | None = Field(default=None, min_length=1, max_length=10)
    planning_mode: Literal['auto', 'model', 'fixed'] = 'auto'


class CopilotRequest(StrictModel):
    query: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(default="default_session", max_length=100)
    persona_id: str = Field(default="uap", max_length=50)
    product_ids: list[Annotated[int, Field(ge=1)]] | None = Field(default=None, min_length=1, max_length=10)
    planning_mode: Literal['auto', 'model', 'fixed'] = 'auto'


class ScopedSearchRequest(SearchIntent):
    product_ids: list[Annotated[int, Field(ge=1)]] | None = Field(default=None, min_length=1, max_length=10)


@router.get('/research/demo')
def prepared_demo():
    from skintellect.research.study import readiness
    return readiness(get_catalog().path)


@router.get('/research/references')
def reference_notes(q: str | None = Query(default=None, max_length=2000)):
    from skintellect.research.references import references
    return {
        'references': references(get_catalog().path, q),
        'notice': 'Background references are not catalog-product verification.'
    }


@router.get('/products/{product_id}/connections')
def product_connections(product_id: int, limit: int = Query(5, ge=1, le=10)):
    from skintellect.research.connections import connections
    result = connections(product_id, get_catalog().path, limit)
    if result is None:
        raise HTTPException(404, detail='Product not found')
    return result


class PreparationRequest(BaseModel):
    kind: Literal['reviews', 'embed']
    limit: int = Field(default=20, ge=1, le=5000)
    product_id: int | None = Field(default=None, ge=1)
    max_calls: int = Field(default=8, ge=1, le=1000)
    max_seconds: int = Field(default=120, ge=10, le=3600)


@router.get('/research/progress')
def preparation_progress():
    from skintellect.research.jobs import snapshot
    return snapshot(get_catalog().path)


@router.post('/research/jobs', status_code=202)
def start_preparation(payload: PreparationRequest, background_tasks: BackgroundTasks):
    from skintellect.research.jobs import create_job, execute
    try:
        job_id = create_job(
            get_catalog().path,
            payload.kind,
            payload.limit,
            payload.product_id,
            payload.max_calls,
            payload.max_seconds,
        )
    except GeminiUnavailable as exc:
        raise HTTPException(503, detail=str(exc)) from None
    except ValueError as exc:
        raise HTTPException(409 if str(exc) == 'preparation_already_active' else 422, detail=str(exc)) from None
    background_tasks.add_task(execute, get_catalog().path, job_id)
    return {'job_id': job_id, 'status': 'queued'}


@router.post('/research/jobs/{job_id}/cancel')
def cancel_preparation(job_id: int):
    from skintellect.research.jobs import cancel
    if not cancel(get_catalog().path, job_id):
        raise HTTPException(404, detail='Active job not found')
    return {'status': 'cancellation_requested', 'notice': 'The current batch may finish before cancellation.'}


@router.get('/research/status')
def model_status():
    from skintellect.database import database
    client = GeminiClient(get_catalog().path)
    ensure_tables(get_catalog().path)
    result = client.status()
    from skintellect.research.model_steps import REVIEW_VERSION, review_client
    review_model = review_client(get_catalog().path).model
    result['review_model'] = review_model
    result['review_extraction_version'] = REVIEW_VERSION
    with database(get_catalog().path) as c:
        result['live_connection_verified'] = bool(
            c.execute("SELECT 1 FROM gemini_runs WHERE status='ok' AND attempts>0 LIMIT 1").fetchone()
        )
        result['cached_model_reviews'] = c.execute(
            'SELECT COUNT(*) FROM review_aspects WHERE extraction_version=?',
            (REVIEW_VERSION + ':' + review_model,),
        ).fetchone()[0]
        result['indexed_vectors'] = c.execute(
            'SELECT COUNT(*) FROM research_vectors WHERE model=?',
            (client.embedding_model,),
        ).fetchone()[0]
    return result


@router.post('/research/reviews/prepare')
def prepare_model_reviews(payload: ExtractionRequest):
    if not evidence_tools.evidence('product:' + str(payload.product_id)):
        raise HTTPException(404, 'Product not found')
    from skintellect.research.preparation import prepare_reviews
    try:
        with run_budget(max_calls=6, max_seconds=90) as run:
            result = prepare_reviews(get_catalog().path, limit=payload.limit, product_id=payload.product_id)
            return result | {'events': run['events']}
    except GeminiUnavailable as exc:
        raise HTTPException(
            503,
            detail={
                'error_code': str(exc),
                'message': 'Gemini is unavailable. Existing review observations remain available.',
            },
        ) from None


@router.get('/quality')
def quality():
    return audit(get_catalog().path)


@router.post('/search/interpret')
def interpret(payload: QueryRequest):
    return search_tools.interpret(payload.query)


@router.post('/search')
def search(payload: ScopedSearchRequest):
    return search_tools.structured_search(
        SearchIntent(**payload.model_dump(exclude={'product_ids'})),
        getattr(payload, 'product_ids', None),
    )


@router.get('/products/{product_id}/review-insights')
def reviews(product_id: int):
    if not evidence_tools.evidence('product:' + str(product_id)):
        raise HTTPException(404, 'Product not found')
    return review_tools.review_insights(product_id)


@router.post('/alternatives')
def alternatives(payload: AlternativeRequest):
    result = alternative_tools.alternatives(
        payload.product_id, payload.constraints, product_ids=payload.product_ids
    )
    if result is None:
        raise HTTPException(404, 'Product not found')
    return result


@router.get('/evidence/{evidence_id}')
def evidence(evidence_id: str):
    result = evidence_tools.evidence(evidence_id)
    if result is None:
        raise HTTPException(404, 'Evidence not found')
    return result


@router.get('/research/retrieve')
def retrieve(q: str = Query(min_length=1, max_length=2000), limit: int = Query(8, ge=1, le=30)):
    from skintellect.research.retrieval import retrieve_hybrid
    return retrieve_hybrid(q, get_catalog().path, limit=limit)


@router.post('/assistant/query')
def assistant(payload: AssistantRequest):
    return service.assistant_query(payload.query, payload.product_ids, payload.planning_mode)


@router.post('/research/copilot')
def copilot(payload: CopilotRequest):
    from skintellect.agents.copilot import get_or_create_copilot_session
    session = get_or_create_copilot_session(payload.session_id, payload.persona_id)
    return session.ask(payload.query, payload.product_ids, payload.planning_mode, get_catalog().path)


@router.post('/research/copilot/stream')
def copilot_stream(payload: CopilotRequest):
    import json
    from fastapi.responses import StreamingResponse
    from skintellect.agents.copilot import get_or_create_copilot_session

    session = get_or_create_copilot_session(payload.session_id, payload.persona_id)

    def event_generator():
        for event in session.stream_ask(payload.query, payload.product_ids, payload.planning_mode, get_catalog().path):
            yield f"data: {json.dumps(event)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post('/research/copilot/plan')
def copilot_plan(payload: QueryRequest):
    from skintellect.agents.intent import classify_and_plan
    plan = classify_and_plan(payload.query, get_catalog().path)
    return plan.to_dict()


@router.get('/research/copilot/sessions')
def copilot_sessions():
    from skintellect.agents.copilot import list_copilot_sessions
    return list_copilot_sessions()


@router.post('/research/copilot/sessions/new')
def new_copilot_session(persona_id: str = Query('uap', max_length=50)):
    from skintellect.agents.copilot import create_new_copilot_session
    session = create_new_copilot_session(persona_id=persona_id)
    return {
        'session_id': session.session_id,
        'title': session.title,
        'persona_id': session.persona_id,
        'created_at': session.created_at,
        'updated_at': session.updated_at,
    }


@router.delete('/research/copilot/sessions/{session_id}')
def remove_copilot_session(session_id: str):
    from skintellect.agents.copilot import delete_copilot_session
    if not delete_copilot_session(session_id):
        raise HTTPException(404, detail='Session not found')
    return {'status': 'deleted', 'session_id': session_id}


@router.get('/research/copilot/sessions/{session_id}')
def get_copilot_session(session_id: str):
    from skintellect.agents.copilot import get_or_create_copilot_session
    session = get_or_create_copilot_session(session_id)
    return {
        'session_id': session.session_id,
        'title': session.title,
        'persona_id': session.persona_id,
        'created_at': session.created_at,
        'updated_at': session.updated_at,
        'messages': session.messages,
        'todo_list': session.todo_list,
    }

