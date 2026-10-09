import re

from app.models.conversation import ConversationContext
from app.models.intent import ShoppingIntent
from app.models.product import Product
from app.search.commerce import CommerceSearchService
from app.search.intent import parse_shopping_intent


class ConversationService:
    def __init__(
        self,
        products: list[Product],
        commerce_search: CommerceSearchService,
    ):
        self.products = products
        self.commerce_search = commerce_search

        self.products_by_id = {
            product.id: product
            for product in products
        }

        self.brands = sorted(
            {product.brand for product in products}
        )

    def _current_products(
        self,
        context: ConversationContext,
    ) -> list[Product]:
        return [
            self.products_by_id[product_id]
            for product_id in context.current_product_ids
            if product_id in self.products_by_id
        ]

    def _merge_intent(
        self,
        current: ShoppingIntent,
        update: ShoppingIntent,
    ) -> ShoppingIntent:
        merged = current.model_copy(deep=True)

        fields = [
            "category",
            "brand",
            "min_price",
            "max_price",
            "color",
            "waterproof",
            "lightweight",
            "in_stock",
        ]

        for field in fields:
            value = getattr(update, field)

            if value is not None:
                setattr(
                    merged,
                    field,
                    value,
                )

        merged.needs_clarification = False
        merged.clarification_question = None

        return merged

    @staticmethod
    def _ordinal_product(
        products: list[Product],
        message: str,
    ) -> Product | None:
        ordinal_map = {
            "first": 0,
            "1st": 0,
            "second": 1,
            "2nd": 1,
            "third": 2,
            "3rd": 2,
        }

        for term, index in ordinal_map.items():
            if term in message:
                if index < len(products):
                    return products[index]

        return None

    def handle(
        self,
        message: str,
        context: ConversationContext,
        top_k: int = 5,
    ):
        normalized = message.lower().strip()

        current_products = self._current_products(
            context
        )

        # Compare products
        if "compare" in normalized:
            if len(current_products) < 2:
                return {
                    "action": "answer",
                    "message":
                        "I need at least two current products to compare.",
                    "context": context,
                }

            products_to_compare = current_products[:2]

            return {
                "action": "compare",
                "message":
                    "Here is a comparison of the first two products.",
                "context": context,
                "comparison": products_to_compare,
            }

        # Add product to cart
        #
        # This must come before the cheapest / most expensive
        # answer blocks because a command such as
        # "add the cheapest one to cart" also contains
        # the word "cheapest".
        if re.search(
            r"\b(add|put)\b.*\bcart\b",
            normalized,
        ):
            if not current_products:
                return {
                    "action": "answer",
                    "message":
                        "There is no current product to add.",
                    "context": context,
                }

            product = None

            if (
                "cheaper" in normalized
                or "cheapest" in normalized
            ):
                product = min(
                    current_products,
                    key=lambda item: item.price,
                )

            elif (
                "more expensive" in normalized
                or "most expensive" in normalized
            ):
                product = max(
                    current_products,
                    key=lambda item: item.price,
                )

            else:
                product = self._ordinal_product(
                    current_products,
                    normalized,
                )

            if product is None:
                return {
                    "action": "answer",
                    "message":
                        "Tell me which product to add, "
                        "for example: add the first one to cart.",
                    "context": context,
                }

            if product.inventory <= 0:
                return {
                    "action": "answer",
                    "message":
                        f"{product.title} is currently out of stock.",
                    "context": context,
                }

            return {
                "action": "add_to_cart",
                "message":
                    f"{product.title} was selected for your cart.",
                "context": context,
                "selected_product": product,
            }

        # Cheapest product
        if (
            "cheapest" in normalized
            or "lowest price" in normalized
        ):
            if not current_products:
                return {
                    "action": "answer",
                    "message":
                        "There are no current products to compare.",
                    "context": context,
                }

            product = min(
                current_products,
                key=lambda item: item.price,
            )

            return {
                "action": "answer",
                "message":
                    f"{product.title} is the cheapest "
                    f"at {product.price:.2f} "
                    f"{product.currency}.",
                "context": context,
                "selected_product": product,
            }

        # Most expensive product
        if (
            "most expensive" in normalized
            or "highest price" in normalized
        ):
            if not current_products:
                return {
                    "action": "answer",
                    "message":
                        "There are no current products to compare.",
                    "context": context,
                }

            product = max(
                current_products,
                key=lambda item: item.price,
            )

            return {
                "action": "answer",
                "message":
                    f"{product.title} is the most expensive "
                    f"at {product.price:.2f} "
                    f"{product.currency}.",
                "context": context,
                "selected_product": product,
            }

        # Refine previous shopping intent
        if context.intent is not None:
            follow_up_intent = parse_shopping_intent(
                query=message,
                brands=self.brands,
                require_category=False,
            )

            has_refinement = any(
                [
                    follow_up_intent.category
                    is not None,
                    follow_up_intent.brand
                    is not None,
                    follow_up_intent.min_price
                    is not None,
                    follow_up_intent.max_price
                    is not None,
                    follow_up_intent.color
                    is not None,
                    follow_up_intent.waterproof
                    is not None,
                    follow_up_intent.lightweight
                    is not None,
                    follow_up_intent.in_stock
                    is not None,
                ]
            )

            if has_refinement:
                merged_intent = self._merge_intent(
                    context.intent,
                    follow_up_intent,
                )

                combined_query = (
                    f"{context.original_query or ''} "
                    f"{message}"
                ).strip()

                result = (
                    self.commerce_search.search_with_intent(
                        query=combined_query,
                        intent=merged_intent,
                        top_k=top_k,
                    )
                )

                product_ids = [
                    item["product"].id
                    for item in result["results"]
                ]

                new_context = ConversationContext(
                    original_query=combined_query,
                    intent=merged_intent,
                    current_product_ids=product_ids,
                )

                return {
                    "action": "refine",
                    "message":
                        f"I refined the products using: {message}",
                    "context": new_context,
                    "results": result["results"],
                }

        # Otherwise treat it as a new product search
        result = self.commerce_search.search(
            query=message,
            top_k=top_k,
        )

        intent = ShoppingIntent(
            **result["intent"]
        )

        if result["needs_clarification"]:
            new_context = ConversationContext(
                original_query=message,
                intent=intent,
                current_product_ids=[],
            )

            return {
                "action": "clarify",
                "message":
                    result["clarification_question"],
                "context": new_context,
            }

        product_ids = [
            item["product"].id
            for item in result["results"]
        ]

        new_context = ConversationContext(
            original_query=message,
            intent=intent,
            current_product_ids=product_ids,
        )

        return {
            "action": "search",
            "message":
                f"I found {len(product_ids)} matching products.",
            "context": new_context,
            "results": result["results"],
        }