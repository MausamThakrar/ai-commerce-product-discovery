# AI Commerce Product Discovery

An AI-powered ecommerce product discovery system that understands natural-language shopping requests, combines keyword and semantic retrieval, applies hard commerce constraints, and asks for clarification when a shopper's intent is ambiguous.

The goal is to build a reusable product-discovery engine for ecommerce rather than a platform-specific implementation.

## Current capabilities

The project currently supports:

- Synthetic ecommerce catalog with products, variants, inventory, attributes, brands, categories, and pricing
- TF-IDF keyword search baseline
- Semantic search using sentence-transformer embeddings
- Hybrid keyword + semantic ranking
- Hard ecommerce constraints for:
  - category
  - brand
  - minimum price
  - maximum price
  - color
  - waterproof
  - lightweight
  - inventory availability
- Natural-language shopping intent extraction
- Category recognition
- Price extraction
- Product attribute extraction
- Ambiguity detection
- Clarification questions
- Commerce-aware search API
- Automated tests

## Example

A shopper can search with:

```text
black waterproof hiking shoes under €120
```

The system extracts structured commerce intent:

```json
{
  "category": "trail-shoes",
  "brand": null,
  "min_price": null,
  "max_price": 120,
  "color": "black",
  "waterproof": true,
  "lightweight": null,
  "in_stock": null
}
```

These constraints are applied as hard filters before recommendations are returned.

This prevents semantically relevant but commercially invalid products from being recommended.

For example, a highly relevant €180 shoe cannot appear when the shopper explicitly requests products under €120.

## Ambiguous queries

Semantic similarity alone can produce misleading ecommerce recommendations when the shopper has not specified a product type.

For example:

```text
something light for walking through wet mountains
```

The system can understand:

```text
lightweight = true
waterproof = true
```

but the shopper may be looking for footwear, clothing, a backpack, or camping equipment.

Instead of blindly returning the products with the highest embedding similarity, the commerce layer can respond with a clarification request:

```text
What type of product are you looking for:
footwear, a jacket, a backpack, or camping equipment?
```

## Search architecture

```text
Natural-language query
        |
        v
Shopping intent parser
        |
        +---- category
        +---- brand
        +---- price range
        +---- color
        +---- waterproof
        +---- lightweight
        +---- availability
        |
        v
Ambiguity check
        |
   +----+----+
   |         |
clarify    search
             |
             v
     Keyword retrieval
          +
     Semantic retrieval
             |
             v
       Hybrid ranking
             |
             v
    Hard commerce filters
             |
             v
      Product results
```

## Retrieval methods

### Keyword search

The keyword baseline uses TF-IDF with unigram and bigram features.

It performs well when the shopper's language closely matches catalog text.

### Semantic search

Semantic search uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Product embeddings include information such as:

- title
- description
- category
- brand
- tags
- structured attributes

This allows conceptually similar products to be retrieved even when exact keywords differ.

### Hybrid search

The commerce search layer combines both retrieval signals.

Current default weighting:

```text
Semantic: 65%
Keyword:  35%
```

Scores are normalized before being combined.

The weighting is currently a product-level default and can be tuned later.

## Hard constraints vs relevance

A key design principle is the separation between:

```text
Relevance
```

and:

```text
Eligibility
```

Keyword and semantic scores determine how relevant a product is.

Commerce constraints determine whether the product is allowed to appear at all.

For example:

```text
Query:
waterproof hiking shoes under €120
```

A product must satisfy the requested category, waterproof requirement, and price ceiling before ranking matters.

## API

The backend is built with FastAPI.

### Health

```http
GET /health
```

### Products

```http
GET /products
```

### Keyword search

```http
GET /search?q=mountain+walking
```

### Semantic search

```http
GET /search/semantic?q=something+for+wet+mountain+walks
```

### Commerce search

```http
GET /search/commerce?q=black+waterproof+hiking+shoes+under+€120
```

Commerce search automatically:

1. interprets the natural-language query
2. extracts structured shopping constraints
3. checks whether the request is sufficiently clear
4. asks for clarification when necessary
5. performs hybrid retrieval
6. enforces hard commerce constraints
7. returns ranked products

## Example commerce response

```json
{
  "query": "black waterproof hiking shoes under €120",
  "intent": {
    "category": "trail-shoes",
    "brand": null,
    "min_price": null,
    "max_price": 120.0,
    "color": "black",
    "waterproof": true,
    "lightweight": null,
    "in_stock": null,
    "category_candidates": [
      "trail-shoes"
    ],
    "needs_clarification": false,
    "clarification_question": null
  },
  "needs_clarification": false,
  "clarification_question": null,
  "results": []
}
```

Actual results depend on products available in the generated catalog.

## Catalog

The current development catalog contains 120 deterministic synthetic products across:

```text
trail-shoes
hiking-jackets
backpacks
camping
```

Products contain ecommerce-oriented data including:

- brand
- category
- price
- currency
- inventory
- tags
- attributes
- variants
- SKUs
- option values

The synthetic catalog keeps development reproducible while the core architecture remains independent of a specific ecommerce platform.

## Project structure

```text
ai-commerce-product-discovery/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── models/
│   │   │   ├── product.py
│   │   │   └── intent.py
│   │   │
│   │   ├── search/
│   │   │   ├── keyword.py
│   │   │   ├── semantic.py
│   │   │   ├── hybrid.py
│   │   │   ├── filters.py
│   │   │   ├── intent.py
│   │   │   └── commerce.py
│   │   │
│   │   └── services/
│   │       └── catalog.py
│   │
│   ├── data/
│   │   └── products.json
│   │
│   ├── scripts/
│   │   └── generate_catalog.py
│   │
│   ├── tests/
│   │   ├── test_keyword_search.py
│   │   ├── test_semantic_search.py
│   │   ├── test_hybrid_search.py
│   │   └── test_intent.py
│   │
│   └── pytest.ini
│
├── requirements.txt
└── README.md
```

## Running locally

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
cd backend
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Tests

Run:

```bash
cd backend
python -m pytest
```

Current test suite:

```text
10 passed
```

The tests cover:

- keyword retrieval
- semantic retrieval
- hybrid retrieval
- hard commerce constraints
- structured intent extraction
- price parsing
- natural category inference
- ambiguous-query detection

## Current development status

### Completed

**Foundation**

- Ecommerce product model
- Synthetic product catalog
- FastAPI backend

**Search**

- Keyword retrieval
- Semantic retrieval
- Hybrid retrieval
- Score normalization
- Ecommerce filters

**Shopping intelligence**

- Natural-language intent parsing
- Category recognition
- Attribute extraction
- Price constraints
- Brand recognition
- Ambiguity detection
- Clarification handling
- Commerce search orchestration

### Next

The next stage turns the backend into a complete shopping experience:

```text
Storefront interface
        ↓
Conversational product discovery
        ↓
Product comparison and refinement
        ↓
Cart actions
        ↓
Catalog import / ecommerce integrations
        ↓
Deployment and portfolio demo
```

## Planned product experience

The finished application is intended to support interactions such as:

```text
Shopper:
I need waterproof hiking shoes under €120.

Assistant:
[matching products]

Shopper:
Which one is the lightest?

Assistant:
[comparison using previous recommendations]

Shopper:
Show me something similar in black.

Assistant:
[refined recommendations]

Shopper:
Compare the first two.

Assistant:
[structured comparison]

Shopper:
Add the cheaper one to my cart.

Assistant:
[cart updated]
```

## Technology

```text
Python
FastAPI
Pydantic
scikit-learn
sentence-transformers
NumPy
pytest
```

Frontend and deployment tooling will be added in the next development stages.

## Project goal

This project is being built as a production-oriented AI commerce application rather than a standalone machine-learning experiment.

The focus is on combining AI retrieval with actual ecommerce requirements such as product attributes, inventory, pricing, shopper constraints, ambiguity, and eventually conversational shopping and cart actions.