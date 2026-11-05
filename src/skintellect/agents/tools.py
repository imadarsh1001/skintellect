"""
LangChain-compatible tools for formulation research, RAG retrieval, and graph exploration.
These tools wrap pure domain and repository operations, exposing typed inputs/outputs.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from skintellect.catalog.store import get_catalog
from skintellect.catalog.products import get_product_by_id, get_products
from skintellect.research.connections import connections as get_connections
from skintellect.research.references import references as get_references
from skintellect.research.reviews import review_insights as get_reviews
from skintellect.research.search import interpret as interpret_search, structured_search
from skintellect.research.models import SearchIntent


class SearchCatalogInput(BaseModel):
    query: str = Field(description="Search keywords or formulation intent, e.g., 'ceramide barrier moisturizer for dry skin'")
    product_ids: Optional[List[int]] = Field(default=None, description="Optional restricted candidate product ID scope")
    category: Optional[str] = Field(default="moisturizers", description="Product category filter")


class IngredientGraphInput(BaseModel):
    product_id: int = Field(description="Product ID to explore ingredient and reference connections for")
    limit: int = Field(default=5, ge=1, le=10, description="Maximum number of connected product paths")


class ReviewInsightsInput(BaseModel):
    product_id: int = Field(description="Product ID to retrieve aspect-based review sentiments and quotes for")


class ReferenceSearchInput(BaseModel):
    query: Optional[str] = Field(default=None, description="Ingredient or topic query to match against scientific references")


# LangChain Tool Decorator Compatibility:
# If langchain_core is installed, use @tool; otherwise provide a transparent decorator that preserves metadata.
try:
    from langchain_core.tools import tool, BaseTool, StructuredTool
    _tool_call = lambda self, *args, **kwargs: (
        self.func(*args, **kwargs) if getattr(self, "func", None) else self.invoke(kwargs if not args else args[0])
    )
    BaseTool.__call__ = _tool_call
    StructuredTool.__call__ = _tool_call
except ImportError:
    def tool(name_or_fn=None, *args, **kwargs):
        def decorator(fn):
            fn.is_tool = True
            fn.tool_name = getattr(fn, '__name__')
            fn.tool_doc = getattr(fn, '__doc__')
            return fn
        if callable(name_or_fn):
            return decorator(name_or_fn)
        return decorator


@tool
def search_catalog_tool(query: str, product_ids: Optional[List[int]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Searches the catalog for products matching intent, ingredient constraints, and categories.
    Returns matching products, constraint satisfaction details, and count.
    """
    path = get_catalog(db_path).path
    interpreted = interpret_search(query, path)
    intent = SearchIntent(**interpreted.get("intent", {}))
    return structured_search(intent, product_ids=product_ids, records=None)


@tool
def get_ingredient_graph_tool(product_id: int, limit: int = 5, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the ingredient relationship graph connecting a product, its shared key ingredients,
    neighboring products sharing the same actives, and scientific evidence references.
    """
    path = get_catalog(db_path).path
    res = get_connections(product_id, path, limit=limit)
    if res is None:
        return {"error": "Product not found", "nodes": [], "edges": []}
    return res


@tool
def get_review_insights_tool(product_id: int, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves aspect-based sentiment analysis (ABSA) observations and verbatim quote excerpts
    from verified real buyer reviews (e.g., texture, hydration, stickiness, pilling, stinging).
    """
    path = get_catalog(db_path).path
    return get_reviews(product_id, path)


@tool
def get_scientific_references_tool(query: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves verified scientific literature and ingredient monograph references
    supporting ingredient functions, efficacy, and safety evidence.
    """
    path = get_catalog(db_path).path
    return get_references(path, query)


@tool
def get_product_detail_tool(product_id: int, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the complete recorded formula, brand, price context, and community ratings for a product.
    """
    return get_product_by_id(product_id)
