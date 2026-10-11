from fastapi import (
    FastAPI,
    HTTPException,
    Query,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.catalog.generic_csv import (
    GenericCsvCatalogAdapter,
)
from app.catalog.generic_json import (
    GenericJsonCatalogAdapter,
)
from app.catalog.shopify import (
    ShopifyCatalogAdapter,
)
from app.models.conversation import (
    ConversationRequest,
)
from app.models.merchant import (
    CatalogImportRequest,
    SearchSettings,
)
from app.services.catalog import (
    ProductCatalog,
)
from app.services.runtime import (
    CommerceRuntime,
)

import os


app = FastAPI(
    title="AI Commerce Product Discovery",
    version="0.7.0",
)

default_origins = (
    "http://localhost:3000,"
    "http://127.0.0.1:3000"
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        default_origins,
    ).split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#
# Runtime
#

demo_catalog = ProductCatalog()

runtime = CommerceRuntime(
    products=demo_catalog.all(),
    source="synthetic-demo",
)


#
# Catalog adapters
#

json_adapter = (
    GenericJsonCatalogAdapter()
)

csv_adapter = (
    GenericCsvCatalogAdapter()
)

shopify_adapter = (
    ShopifyCatalogAdapter()
)


#
# General API
#

@app.get("/health")
def health():
    return {
        "status": "ok",
        "catalog_source":
            runtime.source,
        "products":
            len(runtime.products),
    }


@app.get("/products")
def products():
    return runtime.products


#
# Search APIs
#

@app.get("/search")
def keyword_search_endpoint(
    q: str = Query(
        min_length=1
    ),
    top_k: int | None = Query(
        default=None,
        ge=1,
        le=50,
    ),
):
    result_count = (
        top_k
        or runtime.settings
        .max_recommendations
    )

    results = (
        runtime.keyword_search.search(
            query=q,
            top_k=result_count,
        )
    )

    return {
        "query": q,
        "search_type": "keyword",
        "results_count":
            len(results),
        "results": results,
    }


@app.get("/search/semantic")
def semantic_search_endpoint(
    q: str = Query(
        min_length=1
    ),
    top_k: int | None = Query(
        default=None,
        ge=1,
        le=50,
    ),
):
    result_count = (
        top_k
        or runtime.settings
        .max_recommendations
    )

    results = (
        runtime.semantic_search.search(
            query=q,
            top_k=result_count,
        )
    )

    return {
        "query": q,
        "search_type": "semantic",
        "results_count":
            len(results),
        "results": results,
    }


@app.get("/search/commerce")
def commerce_search_endpoint(
    q: str = Query(
        min_length=1
    ),
    top_k: int | None = Query(
        default=None,
        ge=1,
        le=20,
    ),
):
    result_count = (
        top_k
        or runtime.settings
        .max_recommendations
    )

    return (
        runtime.commerce_search.search(
            query=q,
            top_k=result_count,
        )
    )


#
# Conversation API
#

@app.post("/conversation")
def conversation_endpoint(
    request: ConversationRequest,
):
    result_count = (
        request.top_k
        or runtime.settings
        .max_recommendations
    )

    return (
        runtime.conversation_service
        .handle(
            message=request.message,
            context=request.context,
            top_k=result_count,
        )
    )


#
# Merchant / catalog API
#

@app.get("/merchant/catalog")
def merchant_catalog_status():
    return runtime.status()


@app.post("/merchant/catalog/import")
def import_catalog(
    request: CatalogImportRequest,
):
    try:
        if request.source == "generic-json":
            if request.payload is None:
                raise ValueError(
                    "JSON payload is required."
                )

            products = (
                json_adapter.load(
                    request.payload
                )
            )

        elif request.source == "generic-csv":
            if not request.csv_text:
                raise ValueError(
                    "CSV text is required."
                )

            products = (
                csv_adapter.load(
                    request.csv_text
                )
            )

        elif request.source == "shopify":
            if not isinstance(
                request.payload,
                dict,
            ):
                raise ValueError(
                    "Shopify JSON payload "
                    "is required."
                )

            products = (
                shopify_adapter.load(
                    request.payload
                )
            )

        else:
            raise ValueError(
                "Unsupported catalog source."
            )

        runtime.replace_catalog(
            products=products,
            source=request.source,
        )

        return {
            "message":
                "Catalog imported successfully.",
            "catalog":
                runtime.status(),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/merchant/catalog/reset")
def reset_catalog():
    fresh_demo_catalog = (
        ProductCatalog()
    )

    runtime.replace_catalog(
        products=(
            fresh_demo_catalog.all()
        ),
        source="synthetic-demo",
    )

    return {
        "message":
            "Demo catalog restored.",
        "catalog":
            runtime.status(),
    }


@app.get("/merchant/settings")
def merchant_settings():
    return runtime.settings


@app.put("/merchant/settings")
def update_merchant_settings(
    settings: SearchSettings,
):
    try:
        updated = (
            runtime.update_settings(
                settings
            )
        )

        return {
            "message":
                "Search settings updated.",
            "settings":
                updated,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc