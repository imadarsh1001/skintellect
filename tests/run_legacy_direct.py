"""Run the existing API assertions against service routes without opening sockets.

This validates route behavior and response serialization, not HTTP transport.
Run python -m tests.smoke_api against a live local server for the separate HTTP check.
"""
import inspect
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.params import Param
from pydantic import TypeAdapter

from skintellect.api import catalog as api
from skintellect.config import TEMPLATES_DIR
from tests import smoke_api as test_api


def serialize(value, model):
    adapter = TypeAdapter(model)
    return adapter.dump_python(adapter.validate_python(value), mode='json')


def direct_get(path, timeout=10):
    parsed = urlsplit(path)
    params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    if parsed.path == '/':
        return 200, Path(TEMPLATES_DIR, 'index.html').read_text(encoding='utf-8')
    routes = {'/api/stats': (api.catalog_stats, api.CatalogStats),
              '/api/personas': (api.list_personas, list[api.PersonaModel]),
              '/api/domains': (api.list_domains, dict), '/api/sources': (api.list_sources, dict),
              '/api/products': (api.list_products, api.PaginatedProductsResponse),
              '/api/ingredients': (api.list_ingredients, api.PaginatedIngredientsResponse),
              '/api/ingredients/meta/functions': (api.list_ingredient_functions, dict)}
    if parsed.path in routes:
        function, model = routes[parsed.path]
    elif parsed.path.startswith('/api/products/'):
        function, model = api.get_product_details, api.ProductDetail
        params['product_id'] = parsed.path.rsplit('/', 1)[1]
    elif parsed.path.startswith('/api/ingredients/'):
        function, model = api.get_single_ingredient, api.IngredientDetail
        params['ingredient_id'] = parsed.path.rsplit('/', 1)[1]
    else:
        raise AssertionError('Unmapped direct route: ' + path)
    kwargs = {}
    for name, parameter in inspect.signature(function).parameters.items():
        value = params.get(name, parameter.default)
        if isinstance(value, Param):
            value = value.default
        if name in params and parameter.annotation in (int, float, bool):
            value = value.casefold() == 'true' if parameter.annotation is bool else parameter.annotation(value)
        kwargs[name] = value
    return 200, serialize(function(**kwargs), model)


def direct_post(path, json_data, timeout=10):
    raise AssertionError('Unmapped direct route: ' + path)


if __name__ == '__main__':
    test_api.http_get = direct_get
    test_api.http_post = direct_post
    test_api.wait_for_server = lambda: True
    print('DIRECT ROUTE MODE: HTTP transport is not tested.')
    test_api.run_tests()
