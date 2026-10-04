from fastapi import FastAPI, Query

from app.search.keyword import KeywordSearchEngine
from app.services.catalog import ProductCatalog


app = FastAPI(
    title="AI Commerce Product Discovery",
    version="0.1.0",
)


catalog = ProductCatalog()

keyword_search = KeywordSearchEngine(
    catalog.all()
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "products": len(catalog.all()),
    }


@app.get("/products")
def products():
    return catalog.all()


@app.get("/search")
def search(
    q: str = Query(min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
):
    return {
        "query": q,
        "results": keyword_search.search(
            query=q,
            top_k=top_k,
        ),
    }