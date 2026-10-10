from typing import Any

from pydantic import ValidationError

from app.models.product import Product


class GenericJsonCatalogAdapter:
    """
    Converts generic JSON ecommerce catalog data into
    the application's common Product model.

    Supported payloads:

    [
        {...product...},
        {...product...}
    ]

    or:

    {
        "products": [
            {...product...}
        ]
    }
    """

    source_name = "generic-json"

    def load(
        self,
        payload: Any,
    ) -> list[Product]:

        if isinstance(payload, list):
            raw_products = payload

        elif isinstance(payload, dict):
            raw_products = payload.get(
                "products"
            )

            if not isinstance(
                raw_products,
                list,
            ):
                raise ValueError(
                    "JSON payload must contain "
                    "a 'products' array."
                )

        else:
            raise ValueError(
                "Catalog payload must be "
                "a JSON array or object."
            )

        products: list[Product] = []

        for index, raw_product in enumerate(
            raw_products
        ):
            try:
                product = Product.model_validate(
                    raw_product
                )

            except ValidationError as exc:
                raise ValueError(
                    "Invalid product at index "
                    f"{index}: {exc}"
                ) from exc

            products.append(product)

        if not products:
            raise ValueError(
                "Catalog contains no products."
            )

        return products