"""Check source layout, page assets, documentation and read-only database integrity."""
import ast
import json
import re
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from skintellect.config import DB_PATH, PROJECT_ROOT, STATIC_DIR, TEMPLATES_DIR

ROOT = PROJECT_ROOT


class PageAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            self.ids.append(values['id'])
        if tag in {'script', 'link'}:
            self.assets.append(values.get('src', values.get('href', '')))


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
    node = shutil.which('node')
    js_files = sorted(Path(STATIC_DIR).rglob('*.js'))
    if not node:
        errors.append('Node is required for JavaScript syntax checks.')
    else:
        for path in js_files:
            result = subprocess.run([node, '--check', str(path)], capture_output=True, text=True, timeout=30)
            if result.returncode:
                errors.append(result.stderr)
    pages = []
    for path in sorted(Path(TEMPLATES_DIR).glob('*.html')):
        page = PageAssets()
        page.feed(path.read_text(encoding='utf8'))
        missing = [asset for asset in page.assets if asset.startswith('/static/') and not (Path(STATIC_DIR) / asset.removeprefix('/static/')).is_file()]
        if missing or len(page.ids) != len(set(page.ids)):
            errors.append(f'Page contract failed: {path.name}; missing assets: {missing}')
        pages.append({'page': path.stem, 'missing_assets': missing})
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
        'javascript_syntax_checked': len(js_files),
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
