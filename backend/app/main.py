from fastapi import FastAPI, Query

from app.search.keyword import KeywordSearchEngine
from app.search.semantic import SemanticSearchEngine
from app.services.catalog import ProductCatalog
from app.search.commerce import CommerceSearchService
from app.search.hybrid import HybridSearchEngine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Commerce Product Discovery",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

catalog = ProductCatalog()

keyword_search = KeywordSearchEngine(
    catalog.all()
)

semantic_search = SemanticSearchEngine(
    catalog.all()
)

hybrid_search = HybridSearchEngine(
    products=catalog.all(),
    keyword_search=keyword_search,
    semantic_search=semantic_search,
)


commerce_search = CommerceSearchService(
    products=catalog.all(),
    hybrid_search=hybrid_search,
)

@app.get("/search/commerce")
def commerce_search_endpoint(
    q: str = Query(min_length=1),
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
):
    return commerce_search.search(
        query=q,
        top_k=top_k,
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

@app.get("/search/semantic")
def semantic_search_endpoint(
    q: str = Query(min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
):
    return {
        "query": q,
        "search_type": "semantic",
        "results": semantic_search.search(
            query=q,
            top_k=top_k,
        ),
    }