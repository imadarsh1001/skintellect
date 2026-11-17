"""Vercel Python function entry point.

Vercel auto-detects the ASGI `app` object. The src path is inserted here
explicitly so module resolution never depends solely on dashboard env vars;
PYTHONPATH=src in vercel.json remains as the belt to this suspenders.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from skintellect.api.app import app  # noqa: E402

# Vercel's Python runtime looks for `app` (ASGI) in the handler module.
__all__ = ["app"]
