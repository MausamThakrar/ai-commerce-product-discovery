import json
from pathlib import Path

from app.models.product import Product


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "products.json"
)


class ProductCatalog:
    def __init__(self):
        self.products = self._load_products()

    def _load_products(self) -> list[Product]:
        with DATA_PATH.open() as file:
            data = json.load(file)

        return [
            Product.model_validate(product)
            for product in data
        ]

    def all(self) -> list[Product]:
        return self.products

    def get(self, product_id: str) -> Product | None:
        for product in self.products:
            if product.id == product_id:
                return product

        return None