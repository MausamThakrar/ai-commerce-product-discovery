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
        attributes = " ".join(
            f"{key} {value}"
            for key, value in product.attributes.items()
        )

        return " ".join(
            [
                product.title,
                product.description,
                product.category,
                product.brand,
                " ".join(product.tags),
                attributes,
            ]
        )

    def score_all(self, query: str):
        query_vector = self.vectorizer.transform([query])

        return cosine_similarity(
            query_vector,
            self.product_vectors,
        )[0]

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        scores = self.score_all(query)

        ranked_indices = scores.argsort()[::-1][:top_k]

        return [
            {
                "product": self.products[index],
                "score": float(scores[index]),
            }
            for index in ranked_indices
        ]