"""Offline tests for the product-image proxy endpoint (GET /api/products/{id}/image).

Outbound HTTP is patched (urlopen), the cache dir points at a temp folder, and
the catalog lookup is stubbed — no network, no real database. Same transport
and skip guard as tests/test_research.py's HTTP contracts.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"rest-of-png"

FAKE_URL = "https://storage.skinsort.com/00ujaw042bi4hgwektp7v1b232q3"
FORBIDDEN_URL = "https://evil.example.com/00ujaw042bi4hgwektp7v1b232q3"


@unittest.skipIf(os.environ.get('SKINTELLECT_SKIP_HTTP') == '1', 'Sandbox loopback sockets are unavailable; run this test locally.')
class ProductImageProxyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache_dir = Path(self.temp.name) / 'cache'

        def _urlopen_stub(request, timeout=None):
            if not str(request.get_full_url()).startswith(FAKE_URL):
                raise AssertionError(f'unexpected outbound request: {request.get_full_url()}')

            class FakeResponse:
                def read(self):
                    return PNG_BYTES

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return FakeResponse()

        self.urlopen_patcher = patch('urllib.request.urlopen', side_effect=_urlopen_stub)
        self.urlopen_patcher.start()
        self.addCleanup(self.urlopen_patcher.stop)

        self.lookup_patcher = patch('skintellect.api.catalog.get_product_image_url', return_value=FAKE_URL)
        self.lookup_patcher.start()
        self.addCleanup(self.lookup_patcher.stop)

        self.cache_patcher = patch('skintellect.config.IMAGE_CACHE_DIR', str(self.cache_dir))
        self.cache_patcher.start()
        self.addCleanup(self.cache_patcher.stop)

    def _get(self, product_id: int):
        import asyncio

        import httpx

        from skintellect.api.app import app

        async def exercise():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as c:
                return await c.get(f'/api/products/{product_id}/image')

        return asyncio.run(exercise())

    def test_first_request_fetches_caches_and_serves(self):
        response = self._get(1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'image/png')
        self.assertEqual(response.content, PNG_BYTES)
        self.assertTrue((self.cache_dir / '1').exists())

    def test_second_request_serves_from_cache_without_outbound_fetch(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / '1').write_bytes(PNG_BYTES)
        with patch('skintellect.api.catalog._fetch_image_bytes', side_effect=AssertionError('cache hit must not fetch')):
            response = self._get(1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, PNG_BYTES)

    def test_non_allowlisted_image_host_is_rejected(self):
        from skintellect.api import catalog
        with patch.object(catalog, 'get_product_image_url', return_value=FORBIDDEN_URL):
            response = self._get(2)
        self.assertEqual(response.status_code, 400)

    def test_product_without_image_is_404(self):
        from skintellect.api import catalog
        with patch.object(catalog, 'get_product_image_url', return_value=None):
            response = self._get(3)
        self.assertEqual(response.status_code, 404)

    def test_fetch_failure_maps_to_502(self):
        from skintellect.api import catalog
        with patch.object(catalog, '_fetch_image_bytes', side_effect=OSError('upstream down')):
            response = self._get(4)
        self.assertEqual(response.status_code, 502)

    def test_fetch_leaves_no_tmp_file_behind(self):
        self._get(5)
        leftovers = [p.name for p in self.cache_dir.iterdir() if p.name.startswith('.')]
        self.assertEqual(leftovers, [])


if __name__ == '__main__':
    unittest.main()
