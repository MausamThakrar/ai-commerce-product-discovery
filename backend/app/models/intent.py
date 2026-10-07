from pydantic import BaseModel, Field


class ShoppingIntent(BaseModel):
    category: str | None = None
    brand: str | None = None

    min_price: float | None = None
    max_price: float | None = None

    color: str | None = None

    waterproof: bool | None = None
    lightweight: bool | None = None
    in_stock: bool | None = None

    category_candidates: list[str] = Field(
        default_factory=list
    )

    needs_clarification: bool = False

    clarification_question: str | None = None