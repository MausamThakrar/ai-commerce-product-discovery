import json
from pathlib import Path

from app.catalog.generic_csv import (
    GenericCsvCatalogAdapter,
)
from app.catalog.generic_json import (
    GenericJsonCatalogAdapter,
)
from app.catalog.shopify import (
    ShopifyCatalogAdapter,
)


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "import_examples"
)


def test_generic_json_adapter():
    payload = json.loads(
        (
            DATA_DIR
            / "generic-products.json"
        ).read_text()
    )

    adapter = (
        GenericJsonCatalogAdapter()
    )

    products = adapter.load(
        payload
    )

    assert len(products) == 2

    assert (
        products[0].category
        == "trail-shoes"
    )

    assert (
        products[0]
        .attributes["waterproof"]
        is True
    )

    assert (
        products[0]
        .attributes["color"]
        == "black"
    )


def test_generic_csv_adapter():
    csv_text = (
        DATA_DIR
        / "generic-products.csv"
    ).read_text()

    adapter = (
        GenericCsvCatalogAdapter()
    )

    products = adapter.load(
        csv_text
    )

    assert len(products) == 2

    assert (
        products[0].price
        == 119.90
    )

    assert (
        products[0]
        .attributes["lightweight"]
        is True
    )

    assert (
        products[1].category
        == "backpacks"
    )


def test_shopify_adapter():
    payload = json.loads(
        (
            DATA_DIR
            / "shopify-products.json"
        ).read_text()
    )

    adapter = (
        ShopifyCatalogAdapter()
    )

    products = adapter.load(
        payload
    )

    assert len(products) == 1

    product = products[0]

    assert (
        product.id
        == "gid://shopify/Product/1001"
    )

    assert (
        product.category
        == "trail-shoes"
    )

    assert (
        product.brand
        == "North Demo"
    )

    assert product.price == 129.90

    assert (
        product.attributes[
            "waterproof"
        ]
        is True
    )

    assert (
        product.attributes[
            "lightweight"
        ]
        is True
    )

    assert (
        product.attributes[
            "color"
        ]
        == "black"
    )

    assert len(
        product.variants
    ) == 2


def test_json_adapter_rejects_empty_catalog():
    adapter = (
        GenericJsonCatalogAdapter()
    )

    try:
        adapter.load(
            {
                "products": []
            }
        )

    except ValueError as exc:
        assert (
            "no products"
            in str(exc).lower()
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_csv_adapter_rejects_missing_columns():
    adapter = (
        GenericCsvCatalogAdapter()
    )

    bad_csv = (
        "id,title,price\n"
        "1,Product,10\n"
    )

    try:
        adapter.load(
            bad_csv
        )

    except ValueError as exc:
        assert (
            "missing required columns"
            in str(exc).lower()
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )