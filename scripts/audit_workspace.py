"""Check source layout, documentation links and read-only database integrity."""
import ast
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import sys

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from skintellect.config import DB_PATH, PROJECT_ROOT

ROOT = PROJECT_ROOT


def main():
    errors = []
    python_files = [p for folder in ('src', 'scripts', 'tests') for p in (ROOT / folder).rglob('*.py')]
    legacy = {'agents', 'analysis', 'backend', 'core', 'crawler', 'ingestion', 'pipeline'}
    for path in python_files:
        try:
            tree = ast.parse(path.read_text(encoding='utf-8-sig'), str(path))
            for node in ast.walk(tree):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
                if any(name.split('.')[0] in legacy for name in names):
                    errors.append(f'Legacy import in {path.relative_to(ROOT)}:{node.lineno}')
        except SyntaxError as exc:
            errors.append(str(exc))
    # The legacy templates/static tree was retired in Stage 5; JavaScript
    # syntax and UI semantics now run through tests/check_ui_semantics.js in
    # the aggregate gate, so only Python, links and the database are audited here.
    pages = []
    broken_links = []
    for path in [ROOT / 'README.md', ROOT / 'reports/README.md', ROOT / 'data/README.md', *sorted((ROOT / 'docs').rglob('*.md'))]:
        for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf8')):
            if '://' in target or target.startswith(('#', 'mailto:', 'sandbox:')):
                continue
            target = target.split('#')[0]
            if target and not (path.parent / target).exists():
                broken_links.append({'file': str(path.relative_to(ROOT)), 'target': target})
    errors.extend('Broken link: ' + str(item) for item in broken_links)
    connection = sqlite3.connect(Path(DB_PATH).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        integrity = connection.execute('PRAGMA integrity_check').fetchone()[0]
    finally:
        connection.close()
    if integrity != 'ok':
        errors.append('Database integrity check failed: ' + integrity)
    report = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'all_checked_contracts_passed': not errors,
        'errors': errors,
        'python_sources_compiled': len(python_files),
        'javascript_syntax_checked': 'moved to tests/check_ui_semantics.js',
        'html_contracts': pages,
        'broken_document_links': broken_links,
        'database_integrity': integrity,
        'provider_calls': 0,
        'browser_layout_tested': False,
    }
    output = ROOT / 'reports/latest/workspace-audit.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
