import pytest

from app.models.merchant import SearchSettings
from app.models.product import Product
from app.services.runtime import CommerceRuntime


def make_product(
    product_id: str,
    title: str,
    *,
    category: str = "trail-shoes",
    brand: str = "Test Brand",
    price: float = 99.0,
    inventory: int = 10,
) -> Product:
    return Product(
        id=product_id,
        title=title,
        description=f"{title} test product",
        category=category,
        brand=brand,
        price=price,
        currency="EUR",
        tags=["test"],
        attributes={
            "color": "black",
            "waterproof": True,
            "lightweight": True,
            "use_case": "testing",
        },
        inventory=inventory,
        variants=[],
    )


def test_runtime_status_reflects_catalog():
    products = [
        make_product(
            "shoe-1",
            "Test Trail Shoe",
        ),
        make_product(
            "pack-1",
            "Test Backpack",
            category="backpacks",
            inventory=0,
        ),
    ]

    runtime = CommerceRuntime(
        products=products,
        source="test-catalog",
    )

    status = runtime.status()

    assert status["source"] == "test-catalog"
    assert status["product_count"] == 2
    assert status["products_in_stock"] == 1
    assert status["category_count"] == 2
    assert status["brand_count"] == 1

    assert status["categories"] == [
        "backpacks",
        "trail-shoes",
    ]


def test_catalog_replacement_rebuilds_runtime_services():
    runtime = CommerceRuntime(
        products=[
            make_product(
                "old-1",
                "Old Product",
            )
        ],
        source="old-source",
    )

    old_keyword = runtime.keyword_search
    old_semantic = runtime.semantic_search
    old_hybrid = runtime.hybrid_search
    old_commerce = runtime.commerce_search
    old_conversation = (
        runtime.conversation_service
    )

    replacement = [
        make_product(
            "new-1",
            "New Product",
            brand="New Brand",
        )
    ]

    runtime.replace_catalog(
        products=replacement,
        source="generic-json",
    )

    assert runtime.source == "generic-json"
    assert runtime.products == replacement

    assert (
        runtime.keyword_search
        is not old_keyword
    )

    assert (
        runtime.semantic_search
        is not old_semantic
    )

    assert (
        runtime.hybrid_search
        is not old_hybrid
    )

    assert (
        runtime.commerce_search
        is not old_commerce
    )

    assert (
        runtime.conversation_service
        is not old_conversation
    )

    status = runtime.status()

    assert status["product_count"] == 1
    assert status["brands"] == [
        "New Brand"
    ]


def test_settings_update_normalizes_weights_without_rebuilding_embeddings():
    runtime = CommerceRuntime(
        products=[
            make_product(
                "shoe-1",
                "Test Shoe",
            )
        ],
        source="test",
    )

    old_keyword = runtime.keyword_search
    old_semantic = runtime.semantic_search
    old_hybrid = runtime.hybrid_search
    old_commerce = runtime.commerce_search
    old_conversation = (
        runtime.conversation_service
    )

    updated = runtime.update_settings(
        SearchSettings(
            max_recommendations=3,
            semantic_weight=0.8,
            keyword_weight=0.8,
            hide_unavailable=False,
        )
    )

    assert (
        updated.max_recommendations
        == 3
    )

    assert (
        updated.semantic_weight
        == pytest.approx(0.5)
    )

    assert (
        updated.keyword_weight
        == pytest.approx(0.5)
    )

    assert (
        updated.hide_unavailable
        is False
    )

    # The catalog has not changed, so the
    # expensive retrieval indexes remain.
    assert (
        runtime.keyword_search
        is old_keyword
    )

    assert (
        runtime.semantic_search
        is old_semantic
    )

    # Ranking-dependent services are rebuilt.
    assert (
        runtime.hybrid_search
        is not old_hybrid
    )

    assert (
        runtime.commerce_search
        is not old_commerce
    )

    assert (
        runtime.conversation_service
        is not old_conversation
    )


def test_settings_reject_zero_total_search_weight():
    runtime = CommerceRuntime(
        products=[
            make_product(
                "shoe-1",
                "Test Shoe",
            )
        ],
        source="test",
    )

    with pytest.raises(
        ValueError,
        match="At least one search weight",
    ):
        runtime.update_settings(
            SearchSettings(
                semantic_weight=0,
                keyword_weight=0,
            )
        )