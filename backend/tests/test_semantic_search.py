from app.search.semantic import SemanticSearchEngine
from app.services.catalog import ProductCatalog


def test_semantic_search_returns_results():
    catalog = ProductCatalog()

    search_engine = SemanticSearchEngine(
        catalog.all()
    )

    results = search_engine.search(
        "something light for walking through wet mountains",
        top_k=5,
    )

    assert len(results) == 5


def test_semantic_results_have_scores():
    catalog = ProductCatalog()

    search_engine = SemanticSearchEngine(
        catalog.all()
    )

    results = search_engine.search(
        "something for hiking in rainy weather",
        top_k=5,
    )

    for result in results:
        assert "score" in result
        assert isinstance(result["score"], float)