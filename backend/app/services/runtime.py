from app.models.merchant import SearchSettings
from app.models.product import Product
from app.search.commerce import CommerceSearchService
from app.search.conversation import ConversationService
from app.search.hybrid import HybridSearchEngine
from app.search.keyword import KeywordSearchEngine
from app.search.semantic import SemanticSearchEngine


class CommerceRuntime:
    def __init__(
        self,
        products: list[Product],
        source: str = "synthetic-demo",
        settings: SearchSettings | None = None,
    ):
        self.settings = (
            settings
            or SearchSettings()
        )

        self.source = source
        self.products: list[Product] = []

        self.keyword_search = None
        self.semantic_search = None
        self.hybrid_search = None
        self.commerce_search = None
        self.conversation_service = None

        self.replace_catalog(
            products=products,
            source=source,
        )

    def _build_retrieval(self):
        self.keyword_search = (
            KeywordSearchEngine(
                self.products
            )
        )

        self.semantic_search = (
            SemanticSearchEngine(
                self.products
            )
        )

        self._build_services()

    def _build_services(self):
        self.hybrid_search = (
            HybridSearchEngine(
                products=self.products,
                keyword_search=(
                    self.keyword_search
                ),
                semantic_search=(
                    self.semantic_search
                ),
                keyword_weight=(
                    self.settings
                    .keyword_weight
                ),
                semantic_weight=(
                    self.settings
                    .semantic_weight
                ),
            )
        )

        self.commerce_search = (
            CommerceSearchService(
                products=self.products,
                hybrid_search=(
                    self.hybrid_search
                ),
                hide_unavailable=(
                    self.settings
                    .hide_unavailable
                ),
            )
        )

        self.conversation_service = (
            ConversationService(
                products=self.products,
                commerce_search=(
                    self.commerce_search
                ),
            )
        )

    def replace_catalog(
        self,
        products: list[Product],
        source: str,
    ):
        if not products:
            raise ValueError(
                "Catalog must contain "
                "at least one product."
            )

        self.products = list(products)
        self.source = source

        self._build_retrieval()

    def update_settings(
        self,
        settings: SearchSettings,
    ) -> SearchSettings:

        total_weight = (
            settings.semantic_weight
            + settings.keyword_weight
        )

        if total_weight <= 0:
            raise ValueError(
                "At least one search weight "
                "must be greater than zero."
            )

        normalized = (
            settings.model_copy(
                update={
                    "semantic_weight":
                        settings.semantic_weight
                        / total_weight,

                    "keyword_weight":
                        settings.keyword_weight
                        / total_weight,
                }
            )
        )

        self.settings = normalized

        # Product embeddings do not need
        # rebuilding when only ranking /
        # merchant settings change.
        self._build_services()

        return self.settings

    def status(self) -> dict:
        categories = sorted(
            {
                product.category
                for product in self.products
            }
        )

        brands = sorted(
            {
                product.brand
                for product in self.products
            }
        )

        products_in_stock = sum(
            1
            for product in self.products
            if product.inventory > 0
        )

        variants = sum(
            len(product.variants)
            for product in self.products
        )

        return {
            "source": self.source,
            "product_count":
                len(self.products),
            "products_in_stock":
                products_in_stock,
            "variant_count":
                variants,
            "category_count":
                len(categories),
            "brand_count":
                len(brands),
            "categories":
                categories,
            "brands":
                brands,
            "settings":
                self.settings.model_dump(),
        }