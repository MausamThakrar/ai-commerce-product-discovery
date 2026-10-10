from typing import Literal

from pydantic import BaseModel, Field

from app.models.intent import ShoppingIntent
from app.models.product import Product


class ConversationContext(BaseModel):
    original_query: str | None = None

    intent: ShoppingIntent | None = None

    current_product_ids: list[str] = Field(
        default_factory=list
    )


class ConversationRequest(BaseModel):
    message: str

    context: ConversationContext = Field(
        default_factory=ConversationContext
    )

    top_k: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )


class ConversationResponse(BaseModel):
    action: Literal[
        "search",
        "refine",
        "answer",
        "compare",
        "add_to_cart",
        "clarify",
    ]

    message: str

    context: ConversationContext

    results: list[dict] = Field(
        default_factory=list
    )

    comparison: list[Product] = Field(
        default_factory=list
    )

    selected_product: Product | None = None