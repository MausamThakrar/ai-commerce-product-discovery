from app.search.hybrid import HybridSearchEngine
from app.search.keyword import KeywordSearchEngine
from app.search.semantic import SemanticSearchEngine
from app.services.catalog import ProductCatalog


catalog = ProductCatalog()
products = catalog.all()

keyword_search = KeywordSearchEngine(products)
semantic_search = SemanticSearchEngine(products)

hybrid_search = HybridSearchEngine(
    products=products,
    keyword_search=keyword_search,
    semantic_search=semantic_search,
)


def test_hybrid_search_returns_results():
    results = hybrid_search.search(
        "waterproof hiking shoes",
        top_k=5,
    )

    assert len(results) == 5


def test_hard_commerce_filters():
    results = hybrid_search.search(
        query="waterproof hiking shoes",
        top_k=10,
        category="trail-shoes",
        max_price=120,
        waterproof=True,
        in_stock=True,
    )

    assert len(results) > 0

    for result in results:
        product = result["product"]

        assert product.category == "trail-shoes"
        assert product.price <= 120
        assert product.attributes["waterproof"] is True
        assert product.inventory > 0