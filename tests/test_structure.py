"""Regression checks for packaged resources, dependency direction and moved commands."""
import ast
import subprocess
import sys
import unittest
from pathlib import Path

from skintellect.config import PACKAGE_ROOT
from skintellect.research.references import SOURCE_FILE


class StructureTests(unittest.TestCase):
    def test_spa_entrypoint_sources_exist(self):
        """The legacy templates were retired in Stage 5; the UI contract is
        now the Vite SPA entrypoint in the repository frontend tree."""
        frontend = PACKAGE_ROOT.parents[1] / 'frontend'
        entry = frontend / 'index.html'
        self.assertTrue(entry.is_file(), 'frontend/index.html missing')
        self.assertIn('/src/main.ts', entry.read_text(encoding='utf8'))
        self.assertTrue((frontend / 'src' / 'main.ts').is_file())
        self.assertTrue((frontend / 'src' / 'router' / 'index.ts').is_file())
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
