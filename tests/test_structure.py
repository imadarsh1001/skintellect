"""Regression checks for packaged resources, dependency direction and moved commands."""
import ast
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

from skintellect.config import PACKAGE_ROOT, STATIC_DIR, TEMPLATES_DIR
from skintellect.research.references import SOURCE_FILE


class StructureTests(unittest.TestCase):
    def test_bundled_pages_reference_existing_static_assets(self):
        assets = []

        class Parser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                values = dict(attrs)
                if tag in {'script', 'link'}:
                    assets.append(values.get('src', values.get('href', '')))

        pages = list(Path(TEMPLATES_DIR).glob('*.html'))
        self.assertEqual(len(pages), 4)
        for page in pages:
            Parser().feed(page.read_text(encoding='utf8'))
        for asset in assets:
            if asset.startswith('/static/'):
                self.assertTrue((Path(STATIC_DIR) / asset.removeprefix('/static/')).is_file(), asset)
        self.assertTrue(SOURCE_FILE.is_file())

    def test_modern_frontend_dist_assets_and_entrypoint(self):
        from skintellect.api.app import FRONTEND_DIST
        if FRONTEND_DIST.is_dir():
            self.assertTrue((FRONTEND_DIST / "index.html").is_file())
            assets = list((FRONTEND_DIST / "assets").glob("*"))
            self.assertGreater(len(assets), 0)

    def test_lower_level_modules_do_not_import_assistant_workflow(self):
        for path in PACKAGE_ROOT.rglob('*.py'):
            if path.relative_to(PACKAGE_ROOT).parts[0] not in {'catalog', 'formulation', 'ingestion', 'research'} or path.name == 'service.py':
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding='utf8'))):
                if isinstance(node, ast.ImportFrom):
                    self.assertNotEqual(node.module, 'skintellect.research.service', str(path))
                    if node.module == 'skintellect.research':
                        self.assertNotIn('service', [alias.name for alias in node.names], str(path))
                elif isinstance(node, ast.Import):
                    self.assertNotIn('skintellect.research.service', [alias.name for alias in node.names], str(path))

    def test_moved_maintenance_commands_have_no_side_effects_on_help(self):
        for module in ('skintellect.database', 'skintellect.ingestion.maintenance', 'skintellect.ingestion.pubchem', 'skintellect.research.preparation', 'skintellect.research.study'):
            with self.subTest(module=module):
                result = subprocess.run([sys.executable, '-m', module, '--help'], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('usage:', result.stdout)


if __name__ == '__main__':
    unittest.main()
