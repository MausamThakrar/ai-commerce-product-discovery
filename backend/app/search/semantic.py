from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.product import Product


class SemanticSearchEngine:
    def __init__(self, products: list[Product]):
        self.products = products

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.documents = [
            self._product_to_text(product)
            for product in products
        ]

        self.product_embeddings = self.model.encode(
            self.documents,
            normalize_embeddings=True,
        )

    def _product_to_text(self, product: Product) -> str:
        attributes = " ".join(
            f"{key}: {value}"
            for key, value in product.attributes.items()
        )

        return " ".join(
            [
                product.title,
                product.description,
                f"Category: {product.category}",
                f"Brand: {product.brand}",
                " ".join(product.tags),
                attributes,
            ]
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        scores = cosine_similarity(
            query_embedding,
            self.product_embeddings,
        )[0]

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            results.append(
                {
                    "product": self.products[index],
                    "score": float(scores[index]),
                }
            )

        return results