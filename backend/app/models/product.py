from typing import Any

from pydantic import BaseModel, Field


class ProductVariant(BaseModel):
    id: str
    sku: str
    title: str
    price: float
    available: bool = True
    options: dict[str, str] = Field(default_factory=dict)


class Product(BaseModel):
    id: str
    title: str
    description: str

    category: str
    brand: str

    price: float
    currency: str = "EUR"

    tags: list[str] = Field(default_factory=list)

    attributes: dict[str, Any] = Field(default_factory=dict)

    inventory: int = 0

    variants: list[ProductVariant] = Field(default_factory=list)