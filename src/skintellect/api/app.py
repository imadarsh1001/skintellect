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
)
from skintellect.database import migrate as migrate_foundation


class CachedStaticFiles(StaticFiles):
    """Frontend /assets filenames are content-hashed, so each response is
    safe to cache forever. The HTML routes below serve index.html with
    no-cache so browsers never serve it stale (HTMLResponse carries no
    ETag, so no-cache means a full refetch each load)."""

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


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

FRONTEND_DIST = Path(__file__).resolve().parents[3] / "frontend" / "dist"
if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", CachedStaticFiles(directory=str(FRONTEND_DIST / "assets")), name="frontend_assets")

app.include_router(catalog_router)
app.include_router(formulation_router)
app.include_router(research_router)

@app.get('/health')
def health_check():
    return {'status': 'ok', 'app': APP_NAME, 'version': APP_VERSION}

def _serve_spa() -> HTMLResponse:
    """Serve the built SPA for any workspace path with no-cache (it must
    never be served stale — hashed /assets are immutable)."""
    modern_index = FRONTEND_DIST / "index.html"
    if modern_index.is_file():
        with open(modern_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    raise HTTPException(
        status_code=503,
        detail="The web UI is not built yet. Run `npm run build` in frontend/ (or `npm run dev` for development).",
    )


@app.get('/{spa_path:path}', response_class=HTMLResponse)
def serve_spa(spa_path: str):
    """Catch-all SPA route: every non-API GET serves the app — the client
    router owns unknown paths (catch-all → redirect /). Registered after
    the API routers so unknown /api paths keep their JSON 404."""
    if spa_path == 'api' or spa_path.startswith('api/'):
        raise HTTPException(status_code=404, detail='Not Found')
    return _serve_spa()
