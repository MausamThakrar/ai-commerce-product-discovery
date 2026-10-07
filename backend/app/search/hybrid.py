import numpy as np

from app.models.product import Product
from app.search.filters import matches_filters
from app.search.keyword import KeywordSearchEngine
from app.search.semantic import SemanticSearchEngine


class HybridSearchEngine:
    def __init__(
        self,
        products: list[Product],
        keyword_search: KeywordSearchEngine,
        semantic_search: SemanticSearchEngine,
        keyword_weight: float = 0.35,
        semantic_weight: float = 0.65,
    ):
        self.products = products
        self.keyword_search = keyword_search
        self.semantic_search = semantic_search

        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight

    @staticmethod
    def _normalize(scores):
        minimum = scores.min()
        maximum = scores.max()

        if maximum == minimum:
            return np.zeros_like(scores)

        return (scores - minimum) / (
            maximum - minimum
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        category: str | None = None,
        brand: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        color: str | None = None,
        waterproof: bool | None = None,
        lightweight: bool | None = None,
        in_stock: bool | None = None,
    ) -> list[dict]:

        keyword_scores = self._normalize(
            self.keyword_search.score_all(query)
        )

        semantic_scores = self._normalize(
            self.semantic_search.score_all(query)
        )

        combined_scores = (
            keyword_scores * self.keyword_weight
            + semantic_scores * self.semantic_weight
        )

        results = []

        for index, product in enumerate(self.products):

            if not matches_filters(
                product=product,
                category=category,
                brand=brand,
                min_price=min_price,
                max_price=max_price,
                color=color,
                waterproof=waterproof,
                lightweight=lightweight,
                in_stock=in_stock,
            ):
                continue

            results.append(
                {
                    "product": product,
                    "score": float(combined_scores[index]),
                    "keyword_score": float(
                        keyword_scores[index]
                    ),
                    "semantic_score": float(
                        semantic_scores[index]
                    ),
                }
            )

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]