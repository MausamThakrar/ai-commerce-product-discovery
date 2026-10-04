from app.search.keyword import KeywordSearchEngine
from app.services.catalog import ProductCatalog


def test_keyword_search_returns_results():
    catalog = ProductCatalog()

    search_engine = KeywordSearchEngine(
        catalog.all()
    )

    results = search_engine.search(
        "waterproof hiking shoes",
        top_k=5,
    )

    assert len(results) == 5


def test_results_have_scores():
    catalog = ProductCatalog()

    search_engine = KeywordSearchEngine(
        catalog.all()
    )

    results = search_engine.search(
        "trail running",
        top_k=5,
    )

    for result in results:
        assert "score" in result
        assert result["score"] >= 0