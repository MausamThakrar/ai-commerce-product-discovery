from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.product import Product


class KeywordSearchEngine:
    def __init__(self, products: list[Product]):
        self.products = products

        self.documents = [
            self._product_to_text(product)
            for product in products
        ]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )

        self.product_vectors = self.vectorizer.fit_transform(
            self.documents
        )

    def _product_to_text(self, product: Product) -> str:
        return " ".join(
            [
                product.title,
                product.description,
                product.category,
                product.brand,
                " ".join(product.tags),
            ]
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        query_vector = self.vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            self.product_vectors,
        )[0]

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            product = self.products[index]

            results.append(
                {
                    "product": product,
                    "score": float(scores[index]),
                }
            )

        return results