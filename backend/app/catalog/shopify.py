from typing import Any

from app.models.product import (
    Product,
    ProductVariant,
)


def _connection_nodes(
    value: Any,
) -> list[dict]:
    """
    Supports common GraphQL connection shapes:

    {"nodes": [...]}

    and:

    {"edges": [{"node": {...}}]}
    """

    if isinstance(value, list):
        return value

    if not isinstance(value, dict):
        return []

    nodes = value.get("nodes")

    if isinstance(nodes, list):
        return nodes

    edges = value.get("edges")

    if isinstance(edges, list):
        return [
            edge["node"]
            for edge in edges
            if isinstance(edge, dict)
            and isinstance(
                edge.get("node"),
                dict,
            )
        ]

    return []


def _money(
    value: Any,
) -> float:
    """
    Supports:

    "99.90"

    99.90

    {"amount": "99.90"}

    {"amount": 99.90}
    """

    if isinstance(value, dict):
        value = value.get("amount", 0)

    return float(value or 0)


def _attributes_from_tags(
    tags: list[str],
) -> dict:
    """
    Allows demo/catalog tags such as:

    color:black
    waterproof:true
    lightweight:false
    use_case:mountain trekking
    """

    attributes = {}

    boolean_keys = {
        "waterproof",
        "lightweight",
    }

    supported_keys = {
        "color",
        "waterproof",
        "lightweight",
        "use_case",
    }

    for tag in tags:
        if ":" not in tag:
            continue

        key, value = tag.split(
            ":",
            1,
        )

        key = key.strip().lower()
        value = value.strip()

        if key not in supported_keys:
            continue

        if key in boolean_keys:
            normalized = value.lower()

            if normalized in {
                "true",
                "1",
                "yes",
            }:
                attributes[key] = True

            elif normalized in {
                "false",
                "0",
                "no",
            }:
                attributes[key] = False

        else:
            attributes[key] = value

    return attributes


class ShopifyCatalogAdapter:
    """
    Maps Shopify-style product data into
    the common ecommerce Product model.

    The adapter accepts a simplified
    GraphQL-style payload:

    {
        "products": {
            "nodes": [...]
        }
    }

    It also accepts:

    {
        "products": [...]
    }
    """

    source_name = "shopify"

    def load(
        self,
        payload: dict,
    ) -> list[Product]:

        raw_products = payload.get(
            "products"
        )

        products_data = (
            _connection_nodes(
                raw_products
            )
        )

        if not products_data:
            raise ValueError(
                "Shopify payload contains "
                "no products."
            )

        products = [
            self._convert_product(
                raw_product
            )
            for raw_product
            in products_data
        ]

        return products

    def _convert_product(
        self,
        raw_product: dict,
    ) -> Product:

        raw_variants = (
            _connection_nodes(
                raw_product.get(
                    "variants"
                )
            )
        )

        variants = [
            self._convert_variant(
                raw_variant
            )
            for raw_variant
            in raw_variants
        ]

        tags = raw_product.get(
            "tags"
        ) or []

        if isinstance(tags, str):
            tags = [
                tag.strip()
                for tag in tags.split(",")
                if tag.strip()
            ]

        attributes = (
            _attributes_from_tags(tags)
        )

        product_id = str(
            raw_product.get(
                "id",
                "",
            )
        )

        title = (
            raw_product.get(
                "title"
            )
            or "Untitled product"
        )

        description = (
            raw_product.get(
                "description"
            )
            or raw_product.get(
                "descriptionHtml"
            )
            or ""
        )

        category = (
            raw_product.get(
                "productType"
            )
            or "uncategorized"
        )

        brand = (
            raw_product.get(
                "vendor"
            )
            or "Unknown"
        )

        available_variants = [
            variant
            for variant in variants
            if variant.available
        ]

        if variants:
            price = min(
                variant.price
                for variant in variants
            )
        else:
            price = _money(
                raw_product.get(
                    "priceRange",
                    {},
                ).get(
                    "minVariantPrice",
                    {}
                )
                if isinstance(
                    raw_product.get(
                        "priceRange"
                    ),
                    dict,
                )
                else 0
            )

        inventory = (
            len(available_variants)
            if variants
            else 0
        )

        return Product(
            id=product_id,
            title=title,
            description=description,
            category=category,
            brand=brand,
            price=price,
            currency="EUR",
            tags=tags,
            attributes=attributes,
            inventory=inventory,
            variants=variants,
        )

    def _convert_variant(
        self,
        raw_variant: dict,
    ) -> ProductVariant:

        selected_options = (
            raw_variant.get(
                "selectedOptions"
            )
            or []
        )

        options = {
            option.get(
                "name",
                "Option",
            ): option.get(
                "value",
                "",
            )
            for option
            in selected_options
            if isinstance(
                option,
                dict,
            )
        }

        available = bool(
            raw_variant.get(
                "availableForSale",
                True,
            )
        )

        price = _money(
            raw_variant.get(
                "price",
                0,
            )
        )

        return ProductVariant(
            id=str(
                raw_variant.get(
                    "id",
                    "",
                )
            ),
            sku=(
                raw_variant.get(
                    "sku"
                )
                or ""
            ),
            title=(
                raw_variant.get(
                    "title"
                )
                or "Default"
            ),
            price=price,
            available=available,
            options=options,
        )