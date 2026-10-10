from app.models.intent import ShoppingIntent
from app.models.product import Product
from app.search.hybrid import HybridSearchEngine
from app.search.intent import parse_shopping_intent


class CommerceSearchService:
    def __init__(
        self,
        products: list[Product],
        hybrid_search: HybridSearchEngine,
        hide_unavailable: bool = False,
    ):
        self.products = products
        self.hybrid_search = hybrid_search
        self.hide_unavailable = hide_unavailable

        self.brands = sorted(
            {
                product.brand
                for product in products
            }
        )

    def search_with_intent(
        self,
        query: str,
        intent: ShoppingIntent,
        top_k: int = 5,
    ):
        in_stock = intent.in_stock

        if (
            in_stock is None
            and self.hide_unavailable
        ):
            in_stock = True

        results = self.hybrid_search.search(
            query=query,
            top_k=top_k,
            category=intent.category,
            brand=intent.brand,
            min_price=intent.min_price,
            max_price=intent.max_price,
            color=intent.color,
            waterproof=intent.waterproof,
            lightweight=intent.lightweight,
            in_stock=in_stock,
        )

        return {
            "query": query,
            "intent": intent.model_dump(),
            "needs_clarification": False,
            "clarification_question": None,
            "results_count": len(results),
            "results": results,
        }

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):
        intent = parse_shopping_intent(
            query=query,
            brands=self.brands,
        )

        if intent.needs_clarification:
            return {
                "query": query,
                "intent": intent.model_dump(),
                "needs_clarification": True,
                "clarification_question":
                    intent.clarification_question,
                "results": [],
            }

        return self.search_with_intent(
            query=query,
            intent=intent,
            top_k=top_k,
        )