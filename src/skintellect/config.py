"""Load project configuration without executing dotenv values or exposing secrets."""
import os
import re
from pathlib import Path


def load_environment(path=None):
    if path is None and os.environ.get('SKINTELLECT_LOAD_DOTENV', os.environ.get('SKINSORT_LOAD_DOTENV', '1')) == '0':
        return
    path = Path(path) if path else PROJECT_ROOT / '.env'
    if not path.is_file():
        return
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, sep, value = line.removeprefix('export ').partition('=')
        key, value = key.strip(), value.strip()
        if not sep or not re.fullmatch(r'(?:GEMINI_[A-Z0-9_]+|RESEARCH_[A-Z0-9_]+|SKINTELLECT_[A-Z0-9_]+|SKINSORT_[A-Z0-9_]+|GOOGLE_API_KEY|GOOGLE_CLOUD_PROJECT|GOOGLE_CLOUD_LOCATION|API_ENDPOINT|MODEL_ID|GENERATE_CONTENT_API|AGENT_LLM_MODE)', key):
            continue
        if value[:1] in {'"', "'"} and value[-1:] == value[:1]:
            value = value[1:-1]
        else:
            value = value.split(' #', 1)[0].strip()
        if value:
            os.environ.setdefault(key, value)


def llm_enabled():
    load_environment()
    return os.environ.get('RESEARCH_LLM_ENABLED', '1') == '1' and os.environ.get('AGENT_LLM_MODE') != 'offline'


def set_embedding_model(model, path=None):
    """Change only the embedding-model setting; never log credential-file contents."""
    if model not in {'gemini-embedding-001','gemini-embedding-2'}:
        raise ValueError('unsupported_embedding_model')
    path=Path(path) if path else PROJECT_ROOT / '.env'
    content=path.read_text(encoding='utf-8-sig') if path.exists() else ''
    setting='GEMINI_EMBEDDING_MODEL='+model
    pattern=r'(?m)^\s*(?:export )?GEMINI_EMBEDDING_MODEL\s*=.*$'
    if re.search(pattern,content):
        content=re.sub(pattern,setting,content)
    else:
        content=content.rstrip()+'\n'+setting+'\n'
    path.write_text(content,encoding='utf-8')


def set_absa_model(model,path=None):
    """Activate a validated review model without touching other provider settings."""
    if not re.fullmatch(r'[a-zA-Z0-9._-]{1,100}',model):
        raise ValueError('invalid_model_name')
    path=Path(path) if path else PROJECT_ROOT / '.env'
    content=path.read_text(encoding='utf-8-sig') if path.exists() else ''
    setting='GEMINI_ABSA_MODEL='+model
    pattern=r'(?m)^\s*(?:export )?GEMINI_ABSA_MODEL\s*=.*$'
    if re.search(pattern,content):content=re.sub(pattern,setting,content)
    else:content=content.rstrip()+'\n'+setting+'\n'
    path.write_text(content,encoding='utf8')

PACKAGE_ROOT = Path(__file__).resolve().parent
_CHECKOUT = PACKAGE_ROOT.parents[1]
PROJECT_ROOT = Path(os.environ.get("SKINTELLECT_HOME", os.environ.get("SKINSORT_HOME", str(_CHECKOUT if (_CHECKOUT / "pyproject.toml").is_file() else Path.cwd())))).resolve()

import sys
for _extra in [PROJECT_ROOT / ".runtime", PROJECT_ROOT / ".runtime" / "quality"]:
    if _extra.is_dir() and str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

load_environment()

BASE_DIR = str(PROJECT_ROOT)
STATIC_DIR = str(PACKAGE_ROOT / "web" / "static")
TEMPLATES_DIR = str(PACKAGE_ROOT / "web" / "templates")
EXPORTS_DIR = str(PROJECT_ROOT / "data" / "exports")


def resolve_database_path(root: Path = PROJECT_ROOT, override: str | None = None) -> str:
    """Find the historical catalog or use an explicit existing database.

    Relative overrides resolve against the checkout. An invalid explicit path
    fails instead of allowing SQLite to silently create an empty catalog.
    """
    root = Path(root).resolve()
    if override:
        path = Path(override).expanduser()
        path = path if path.is_absolute() else root / path
        if not path.is_file():
            raise FileNotFoundError(f"SKINTELLECT_DB_PATH does not name a file: {path}")
        return str(path.resolve())
    candidates = [
        root / "skintellect_moisturizers.db",
        root / "skintellect.db",
        root / "data" / "skintellect_moisturizers.db",
        root / "data" / "skintellect.db",
        root / "skinsort_moisturizers.db",
        root / "data" / "skinsort_moisturizers.db",
        root / "formulation_studio.db",
        root / "skinsort_products.db",
    ]
    return str(next((p for p in candidates if p.is_file() and p.stat().st_size > 1000), candidates[0]))


DB_PATH = resolve_database_path(override=os.environ.get("SKINTELLECT_DB_PATH") or os.environ.get("SKINSORT_DB_PATH"))
APP_NAME = "Skintellect"
APP_DESCRIPTION = "Evidence-backed product research with explicit unknowns and heuristic assessments"
APP_VERSION = "3.0.0"
