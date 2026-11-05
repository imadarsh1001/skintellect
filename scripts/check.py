"""Run correctness checks against a disposable synthetic catalog, without credentials."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    env = os.environ.copy()
    for name in list(env):
        if name.startswith(("GEMINI_", "GOOGLE_", "RESEARCH_", "SKINTELLECT_", "SKINSORT_")) or name in {
            "API_ENDPOINT", "MODEL_ID", "GENERATE_CONTENT_API", "AGENT_LLM_MODE"
        }:
            env.pop(name)
    env.update({
        "SKINTELLECT_LOAD_DOTENV": "0",
        "SKINSORT_LOAD_DOTENV": "0",
        "RESEARCH_LLM_ENABLED": "0",
        "AGENT_LLM_MODE": "auto",  # Mock-provider tests explicitly enable their own clients.
        "SKINTELLECT_SKIP_HTTP": "1",  # Skip network/loopback socket checks in sandbox
        "SKINSORT_SKIP_HTTP": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1",
    })
    # Support the existing workstation runtime as well as a standard virtual environment.
    paths = [str(ROOT / "src"), str(ROOT)]
    if sys.prefix == sys.base_prefix:
        paths.extend([str(ROOT / ".runtime" / "quality"), str(ROOT / ".runtime")])
    env["PYTHONPATH"] = os.pathsep.join(paths)
    nodejs_dir = r"C:\Program Files\nodejs"
    if os.path.exists(nodejs_dir):
        env["PATH"] = nodejs_dir + os.pathsep + env.get("PATH", "")
    work = ROOT / ".test-work"
    work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="checks-", dir=work) as directory:
        catalog = Path(directory) / "catalog.db"
        catalog.touch()
        env["SKINTELLECT_DB_PATH"] = str(catalog)
        env["SKINSORT_DB_PATH"] = str(catalog)
        env["SKINTELLECT_TEST_TEMP"] = directory
        env["SKINSORT_TEST_TEMP"] = directory
        commands = [
            ["-m", "ruff", "check", "."],
            ["-m", "tests.bootstrap_catalog"],
            ["-m", "unittest", "discover", "-s", "tests", "-t", ".", "-p", "test_*.py", "-v"],
        ]
        for arguments in commands:
            print("Running: python " + " ".join(arguments), flush=True)
            try:
                result = subprocess.run(
                    [sys.executable, *arguments], cwd=ROOT, env=env, timeout=120
                )
            except subprocess.TimeoutExpired:
                print("Check timed out. Verify local event-loop sockets are permitted.")
                return 1
            if result.returncode:
                return result.returncode
        node = shutil.which('node', path=env["PATH"])
        if node:
            print('Running: node tests/check_ui_semantics.js', flush=True)
            result = subprocess.run([node, 'tests/check_ui_semantics.js'], cwd=ROOT, env=env, timeout=30)
            if result.returncode:
                return result.returncode
    print("All offline checks passed; disposable test data cleaned up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
