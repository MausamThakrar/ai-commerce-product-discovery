from typing import Any, Literal

from pydantic import BaseModel, Field


class CatalogImportRequest(BaseModel):
    source: Literal[
        "generic-json",
        "generic-csv",
        "shopify",
    ]

    payload: Any = None
    csv_text: str | None = None


class SearchSettings(BaseModel):
    max_recommendations: int = Field(
        default=6,
        ge=1,
        le=20,
    )

    semantic_weight: float = Field(
        default=0.65,
        ge=0,
        le=1,
    )

    keyword_weight: float = Field(
        default=0.35,
        ge=0,
        le=1,
    )

    hide_unavailable: bool = True