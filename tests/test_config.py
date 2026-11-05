"""Configuration boundaries and compatibility behavior, using disposable files."""

import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skintellect.config import PROJECT_ROOT, load_environment, resolve_database_path


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        parent = Path(os.environ.get("SKINTELLECT_TEST_TEMP", os.environ.get("SKINSORT_TEST_TEMP", PROJECT_ROOT / ".test-work")))
        parent.mkdir(exist_ok=True, parents=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_root_catalog_has_priority_over_data_fallback(self):
        (self.root / "data").mkdir()
        for name in ["skintellect_moisturizers.db", "data/skintellect_moisturizers.db"]:
            (self.root / name).write_bytes(b"x" * 1001)
        self.assertEqual(resolve_database_path(self.root), str(self.root / "skintellect_moisturizers.db"))

    def test_legacy_catalog_fallback(self):
        (self.root / "skinsort_moisturizers.db").write_bytes(b"x" * 1001)
        self.assertEqual(resolve_database_path(self.root), str(self.root / "skinsort_moisturizers.db"))

    def test_empty_root_catalog_does_not_hide_existing_data_catalog(self):
        (self.root / "skintellect_moisturizers.db").touch()
        (self.root / "data").mkdir()
        fallback = self.root / "data/skintellect_moisturizers.db"
        fallback.write_bytes(b"x" * 1001)
        self.assertEqual(resolve_database_path(self.root), str(fallback))

    def test_relative_override_resolves_against_project_root(self):
        path = self.root / "custom.db"
        path.touch()
        self.assertEqual(resolve_database_path(self.root, "custom.db"), str(path))

    def test_missing_override_fails_without_creating_empty_database(self):
        with self.assertRaises(FileNotFoundError):
            resolve_database_path(self.root, "typo.db")
        self.assertFalse((self.root / "typo.db").exists())

    def test_explicit_dotenv_keeps_shell_precedence(self):
        path = self.root / ".env"
        path.write_text("SKINTELLECT_DB_PATH=file.db\nSKINTELLECT_COOKIES='local-session'\n", encoding="utf-8")
        with patch.dict(os.environ, {"SKINTELLECT_DB_PATH": "shell.db"}):
            load_environment(path)
            self.assertEqual(os.environ["SKINTELLECT_DB_PATH"], "shell.db")
            self.assertEqual(os.environ["SKINTELLECT_COOKIES"], "local-session")

    def test_legacy_dotenv_environment_precedence(self):
        path = self.root / ".env"
        path.write_text("SKINSORT_DB_PATH=legacy.db\nSKINSORT_COOKIES='legacy-session'\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SKINTELLECT_DB_PATH", None)
            os.environ.pop("SKINSORT_DB_PATH", None)
            os.environ.pop("SKINSORT_COOKIES", None)
            load_environment(path)
            self.assertEqual(os.environ["SKINSORT_DB_PATH"], "legacy.db")
            self.assertEqual(os.environ["SKINSORT_COOKIES"], "legacy-session")

    def test_dotenv_can_be_disabled_for_offline_checks(self):
        with patch.dict(os.environ, {"SKINTELLECT_LOAD_DOTENV": "0"}):
            with patch("skintellect.config.Path.read_text") as read:
                load_environment()
                read.assert_not_called()

    def test_api_import_from_another_directory_does_not_write_database(self):
        catalog = self.root / "empty.db"
        catalog.touch()
        env = os.environ | {"SKINTELLECT_DB_PATH": str(catalog), "SKINTELLECT_LOAD_DOTENV": "0"}
        env["PYTHONPATH"] = os.pathsep.join([str(PROJECT_ROOT / "src"), env.get("PYTHONPATH", "")])
        result = subprocess.run(
            [sys.executable, "-c", "import skintellect.api.app"],
            cwd=self.root, env=env, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(catalog.stat().st_size, 0)

    def test_runtime_modules_are_owned_by_src_package(self):
        for name in ("skintellect.api.app", "skintellect.catalog.store", "skintellect.formulation.scoring", "skintellect.database"):
            with self.subTest(module=name):
                module = importlib.import_module(name)
                self.assertTrue(Path(module.__file__).is_relative_to(PROJECT_ROOT / "src" / "skintellect"))

    def test_cli_help_renders_root_and_pipeline_command(self):
        for arguments in [["--help"], ["recommend", "--help"]]:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, "-m", "skintellect", *arguments],
                    cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)

    def test_database_init_and_audit_without_network(self):
        from skintellect.database import audit, init_db

        catalog = self.root / "test.db"
        init_db(str(catalog))
        counts = audit(str(catalog))
        self.assertIn("products", counts)
        self.assertEqual(counts["products"], 0)


if __name__ == "__main__":
    unittest.main()
