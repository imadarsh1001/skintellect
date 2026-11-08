import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from skintellect.api.catalog import router as catalog_router
from skintellect.api.formulation import router as formulation_router
from skintellect.api.research import router as research_router
from skintellect.catalog.store import get_catalog
from skintellect.config import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    STATIC_DIR,
    TEMPLATES_DIR,
)
from skintellect.database import migrate as migrate_foundation


@asynccontextmanager
async def lifespan(app):
    from skintellect.research.jobs import recover_interrupted
    from skintellect.research.references import ingest_references
    migrate_foundation(get_catalog().path)
    recover_interrupted(get_catalog().path)
    ingest_references(get_catalog().path)
    yield

app = FastAPI(
    title=APP_NAME + " API",
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

FRONTEND_DIST = Path(__file__).resolve().parents[3] / "frontend" / "dist"
if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="frontend_assets")

app.include_router(catalog_router)
app.include_router(formulation_router)
app.include_router(research_router)

@app.get('/health')
def health_check():
    return {'status': 'ok', 'app': APP_NAME, 'version': APP_VERSION}

@app.get('/progress', response_class=HTMLResponse)
def progress_workspace():
    with open(os.path.join(TEMPLATES_DIR, 'progress.html'), encoding='utf-8') as f:
        return HTMLResponse(f.read())

@app.get('/study', response_class=HTMLResponse)
def prepared_study_workspace():
    with open(os.path.join(TEMPLATES_DIR,'study.html'),encoding='utf-8') as f:
        return HTMLResponse(f.read())

@app.get('/research', response_class=HTMLResponse)
def research_workspace():
    with open(os.path.join(TEMPLATES_DIR, 'research.html'), encoding='utf-8') as f:
        return HTMLResponse(f.read())

@app.get('/compare', response_class=HTMLResponse)
def compare_workspace():
    modern_index = FRONTEND_DIST / "index.html"
    if modern_index.is_file():
        with open(modern_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<meta http-equiv='refresh' content='0; url=/#compare'>")

@app.get('/graph', response_class=HTMLResponse)
def graph_workspace():
    modern_index = FRONTEND_DIST / "index.html"
    if modern_index.is_file():
        with open(modern_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<meta http-equiv='refresh' content='0; url=/#graph'>")

@app.get('/copilot', response_class=HTMLResponse)
def copilot_workspace():
    modern_index = FRONTEND_DIST / "index.html"
    if modern_index.is_file():
        with open(modern_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<meta http-equiv='refresh' content='0; url=/#copilot'>")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    modern_index = FRONTEND_DIST / "index.html"
    if modern_index.is_file():
        with open(modern_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="index.html template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
