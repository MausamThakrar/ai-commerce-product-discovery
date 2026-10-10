# AI Commerce Product Discovery

A conversational AI-powered product discovery and shopping experience for ecommerce.

The application understands natural-language shopping requests, combines lexical and semantic retrieval, applies hard commerce constraints, supports conversational refinement and product comparison, and lets shoppers add recommended products to a cart.

It also includes a merchant-facing catalog management layer that can import different ecommerce data formats, rebuild the search runtime, and configure discovery behavior without restarting the application.

The core architecture is intentionally ecommerce-platform independent. Shopify is supported as one catalog adapter rather than being coupled to the discovery engine.

---

## What the application does

A shopper can start with:

```text
waterproof hiking shoes under €200
```

The system interprets the request, extracts structured shopping constraints and retrieves matching products.

The shopper can then continue:

```text
only black ones
```

The previous search context is retained and refined.

Then:

```text
which is cheapest?
```

The assistant evaluates the current result set.

Then:

```text
compare the first two
```

A structured comparison is displayed.

And:

```text
add the cheapest one to cart
```

The selected product is added to the cart.

On the merchant side, a different product catalog can be imported at runtime:

```text
JSON / CSV / Shopify-style data
              ↓
        Catalog adapter
              ↓
      Common product model
              ↓
       Runtime rebuild
              ↓
Keyword + semantic indexes
              ↓
   Existing storefront search
```

No application restart is required after a catalog import.

---

# Current capabilities

## Product discovery

- Natural-language product search
- TF-IDF keyword retrieval
- Semantic retrieval using sentence-transformer embeddings
- Hybrid keyword + semantic ranking
- Normalized retrieval scores
- Commerce-aware result filtering
- Runtime-configurable retrieval weights
- Runtime-configurable recommendation count

---

## Commerce constraints

The system can enforce:

- category
- brand
- minimum price
- maximum price
- color
- waterproof requirement
- lightweight requirement
- inventory availability

These constraints are treated separately from relevance.

For example:

```text
black waterproof hiking shoes under €120
```

can be interpreted as:

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

A semantically relevant €180 product cannot appear when the shopper explicitly requests products under €120.

---

# Shopping intent and clarification

The intent layer converts natural-language shopping requests into structured ecommerce constraints.

For example:

```text
black waterproof hiking shoes under €120
```

becomes:

```text
category    = trail-shoes
color       = black
waterproof  = true
max_price   = 120
```

The system can also detect when there is not enough information to safely recommend a product type.

For example:

```text
something light for walking through wet mountains
```

can imply:

```text
lightweight = true
waterproof  = true
```

but it does not clearly specify whether the shopper wants footwear, clothing, a backpack or camping equipment.

Instead of blindly returning the highest semantic matches, the application asks for clarification:

```text
What type of product are you looking for:
footwear, a jacket, a backpack, or camping equipment?
```

---

# Conversational shopping

Search state is retained between shopper messages.

Example:

```text
Shopper:
waterproof hiking shoes under €200

Assistant:
I found matching products.

Shopper:
only black ones

Assistant:
I updated the results based on: only black ones

Shopper:
which is cheapest?

Assistant:
WildPath Trail Runner 2 is the cheapest at 92.73 EUR.

Shopper:
compare the first two

Assistant:
Here is a comparison of the first two products.

Shopper:
add the cheapest one to cart

Assistant:
WildPath Trail Runner 2 was selected for your cart.
```

Supported conversational operations include:

- refining previous search constraints
- cheapest product lookup
- most expensive product lookup
- references such as first, second and third product
- comparison of current recommendations
- conversational add-to-cart commands
- continued use of previous shopping intent

Simple commerce operations are handled deterministically rather than delegating every action to a language model.

---

# Product comparison

The storefront can compare products from the current recommendation set.

The comparison uses structured catalog data such as:

```text
Product
Price
Brand
Category
Inventory
Waterproof
Lightweight
Color
Use case
```

This keeps comparison factual and tied directly to product data.

---

# Cart

The frontend includes a client-side shopping cart.

Supported interactions include:

- add product from product details
- add product through conversation
- increase quantity
- decrease quantity
- remove product
- calculate line totals
- calculate cart total

The current cart is intentionally local to the demo application.

A platform-specific cart adapter can be added separately.

---

# Catalog adapters

The discovery engine operates on a common internal `Product` model.

External catalog formats are converted into that model through isolated adapters.

Currently supported:

```text
Generic JSON
Generic CSV
Shopify-style JSON
```

Architecture:

```text
Generic JSON ──────┐
Generic CSV ───────┼──────┐
Shopify data ──────┘      │
                          ▼
                   Catalog adapters
                          │
                          ▼
                  Common Product model
                          │
                          ▼
                    CommerceRuntime
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
       Retrieval layer           Commerce services
```

This means additional sources such as WooCommerce, Magento, BigCommerce, ERP or PIM systems can be added without rewriting the search engine.

---

# Generic JSON import

The JSON adapter supports either:

```json
[
  {
    "id": "product-1",
    "title": "Example Product"
  }
]
```

or:

```json
{
  "products": [
    {
      "id": "product-1",
      "title": "Example Product"
    }
  ]
}
```

Products are validated against the application's Pydantic product model before being accepted.

---

# Generic CSV import

The CSV adapter supports one product per row.

Required columns:

```text
id
title
description
category
brand
price
```

Optional ecommerce fields currently include:

```text
currency
inventory
tags
color
waterproof
lightweight
use_case
```

Tags use `|` as the separator:

```text
trail|rain|mountain
```

Boolean values such as:

```text
true
false
yes
no
1
0
```

are normalized during import.

---

# Shopify catalog adapter

The Shopify adapter maps Shopify-style GraphQL product data into the common product model.

It supports common connection structures such as:

```json
{
  "products": {
    "nodes": []
  }
}
```

and GraphQL edge structures:

```json
{
  "products": {
    "edges": [
      {
        "node": {}
      }
    ]
  }
}
```

The adapter maps fields such as:

```text
Product ID
Title
Description
Product type
Vendor
Tags
Variants
SKU
Price
Availability
Selected options
```

into the application's internal ecommerce model.

For the current portfolio version, Shopify data is imported from a JSON payload. A live Shopify API connection is not required for the core discovery architecture.

---

# Runtime catalog management

Catalog imports do more than replace an in-memory product array.

When a new catalog is loaded, the application rebuilds the services that depend on product data:

```text
Imported catalog
      ↓
Common Product model
      ↓
Keyword index rebuilt
      ↓
Semantic embeddings rebuilt
      ↓
Hybrid engine rebuilt
      ↓
Commerce search rebuilt
      ↓
Conversation service rebuilt
```

The storefront can then search the newly imported catalog immediately.

No FastAPI restart is required.

The demo catalog can also be restored at runtime.

---

# Merchant interface

A dedicated merchant page is available at:

```text
http://localhost:3000/merchant
```

The merchant interface provides:

## Catalog overview

- active catalog source
- number of products
- number of products in stock
- number of variants
- number of categories
- number of brands
- category overview
- brand overview

## Catalog import

Supported sources:

```text
Generic JSON
Generic CSV
Shopify JSON
```

After import, the search runtime is rebuilt automatically.

## Demo reset

The original deterministic demo catalog can be restored from the merchant interface.

## Search configuration

Merchants can configure:

```text
Maximum recommendations
Semantic search weight
Keyword search weight
Hide unavailable products
```

Search weights are normalized by the backend when necessary.

For example:

```text
Semantic = 0.8
Keyword  = 0.8
```

becomes:

```text
Semantic = 0.5
Keyword  = 0.5
```

The embedding index does not need to be rebuilt when only ranking configuration changes.

---

# Application architecture

```text
                         Shopper
                            │
                            ▼
                   Next.js Storefront
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
          Search UI                Conversation UI
              │                           │
              └─────────────┬─────────────┘
                            │
                            ▼
                          FastAPI
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       Commerce Search             Conversation
           Service                    Service
              │                           │
              │                 ┌─────────┴─────────┐
              │                 │                   │
              │              Context             Actions
              │                                     │
              │                          ┌──────────┼──────────┐
              │                          ▼          ▼          ▼
              │                       Refine     Compare      Cart
              │
              ▼
        Shopping Intent
              │
       ┌──────┴───────┐
       ▼              ▼
 Ambiguity        Hard commerce
 detection         constraints
       │              │
       └──────┬───────┘
              ▼
        Hybrid retrieval
          /          \
         ▼            ▼
    TF-IDF          Semantic
    keyword        embeddings
         \            /
          └─────┬────┘
                ▼
         Ranked products
```

Catalog management operates alongside this flow:

```text
                   Merchant UI
                       │
                       ▼
                 Catalog import
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        JSON          CSV        Shopify
          │            │            │
          └────────────┼────────────┘
                       ▼
                 Adapter layer
                       │
                       ▼
              Common Product model
                       │
                       ▼
                CommerceRuntime
                       │
                       ▼
              Search services rebuilt
```

---

# Retrieval methods

## Keyword search

The keyword baseline uses TF-IDF with unigram and bigram features.

It is useful when shopper terminology closely matches catalog text.

---

## Semantic search

Semantic retrieval currently uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The product representation includes:

- title
- description
- category
- brand
- tags
- structured attributes

This allows conceptually related products to be retrieved even when exact terminology differs.

---

## Hybrid search

Keyword and semantic scores are normalized and combined.

Default configuration:

```text
Semantic: 65%
Keyword:  35%
```

These values are configurable through the merchant interface.

---

# Relevance vs eligibility

A central design principle is separating:

```text
Relevance
```

from:

```text
Eligibility
```

Retrieval answers:

> How relevant is this product to the shopper's request?

Commerce constraints answer:

> Is this product allowed to appear at all?

For example:

```text
waterproof hiking shoes under €120
```

requires the product to satisfy category, waterproof and price requirements before its relevance score determines its position.

---

# Frontend

The application frontend is built with Next.js and TypeScript.

Current storefront functionality includes:

- natural-language product search
- example shopping queries
- extracted intent chips
- responsive product cards
- match explanations
- clarification flow
- product detail drawer
- conversational refinement
- structured product comparison
- shopping cart drawer
- quantity management
- loading states
- empty states
- API error handling
- responsive mobile layout

Current merchant functionality includes:

- catalog dashboard
- catalog source overview
- JSON catalog upload
- CSV catalog upload
- Shopify-style catalog upload
- demo catalog restoration
- search configuration
- catalog statistics
- category and brand overview

Storefront:

```text
http://localhost:3000
```

Merchant interface:

```text
http://localhost:3000/merchant
```

---

# API

The backend is built with FastAPI.

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Health

```http
GET /health
```

Returns application health together with current catalog information.

---

## Products

```http
GET /products
```

Returns products from the currently active runtime catalog.

---

## Keyword search

```http
GET /search?q=mountain+walking
```

---

## Semantic search

```http
GET /search/semantic?q=something+for+wet+mountain+walks
```

---

## Commerce search

```http
GET /search/commerce?q=black+waterproof+hiking+shoes+under+€120
```

Commerce search:

1. interprets the natural-language request
2. extracts structured shopping constraints
3. checks whether the product type is sufficiently clear
4. asks for clarification when necessary
5. performs hybrid retrieval
6. applies hard commerce constraints
7. returns ranked products

---

## Conversation

```http
POST /conversation
```

Example:

```json
{
  "message": "only black ones",
  "context": {
    "original_query": "waterproof hiking shoes under €200",
    "intent": {
      "category": "trail-shoes",
      "brand": null,
      "min_price": null,
      "max_price": 200,
      "color": null,
      "waterproof": true,
      "lightweight": null,
      "in_stock": null,
      "category_candidates": [
        "trail-shoes"
      ],
      "needs_clarification": false,
      "clarification_question": null
    },
    "current_product_ids": []
  }
}
```

Possible conversation actions include:

```text
search
refine
answer
compare
add_to_cart
clarify
```

---

# Merchant API

## Catalog status

```http
GET /merchant/catalog
```

Example information returned:

```json
{
  "source": "synthetic-demo",
  "product_count": 120,
  "products_in_stock": 118,
  "variant_count": 0,
  "category_count": 4,
  "brand_count": 5,
  "categories": [],
  "brands": [],
  "settings": {}
}
```

Exact stock totals depend on the generated catalog.

---

## Import catalog

```http
POST /merchant/catalog/import
```

Supported source values:

```text
generic-json
generic-csv
shopify
```

A successful import automatically replaces the runtime catalog and rebuilds retrieval services.

---

## Restore demo catalog

```http
POST /merchant/catalog/reset
```

Restores the bundled deterministic development catalog.

---

## Read search settings

```http
GET /merchant/settings
```

---

## Update search settings

```http
PUT /merchant/settings
```

Example:

```json
{
  "max_recommendations": 6,
  "semantic_weight": 0.65,
  "keyword_weight": 0.35,
  "hide_unavailable": true
}
```

---

# Demo catalog

The bundled development catalog contains 120 deterministic synthetic ecommerce products across:

```text
trail-shoes
hiking-jackets
backpacks
camping
```

Products include:

- ID
- title
- description
- brand
- category
- price
- currency
- inventory
- tags
- structured attributes
- variants
- SKUs
- option values

The synthetic data provides a reproducible development environment.

The runtime is no longer restricted to this catalog because external catalog adapters can replace it dynamically.

---

# Example import catalogs

Example files are included under:

```text
backend/data/import_examples/
```

Current examples:

```text
generic-products.json
generic-products.csv
shopify-products.json
```

These can be used directly from the merchant interface when running the project locally.

---

# Project structure

```text
ai-commerce-product-discovery/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── catalog/
│   │   │   ├── __init__.py
│   │   │   ├── generic_json.py
│   │   │   ├── generic_csv.py
│   │   │   └── shopify.py
│   │   │
│   │   ├── models/
│   │   │   ├── product.py
│   │   │   ├── intent.py
│   │   │   ├── conversation.py
│   │   │   └── merchant.py
│   │   │
│   │   ├── search/
│   │   │   ├── keyword.py
│   │   │   ├── semantic.py
│   │   │   ├── hybrid.py
│   │   │   ├── filters.py
│   │   │   ├── intent.py
│   │   │   ├── commerce.py
│   │   │   └── conversation.py
│   │   │
│   │   └── services/
│   │       ├── catalog.py
│   │       └── runtime.py
│   │
│   ├── data/
│   │   ├── products.json
│   │   └── import_examples/
│   │       ├── generic-products.json
│   │       ├── generic-products.csv
│   │       └── shopify-products.json
│   │
│   ├── scripts/
│   │   └── generate_catalog.py
│   │
│   ├── tests/
│   │   ├── test_keyword_search.py
│   │   ├── test_semantic_search.py
│   │   ├── test_hybrid_search.py
│   │   ├── test_intent.py
│   │   ├── test_conversation.py
│   │   └── test_catalog_adapters.py
│   │
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   ├── globals.css
│   │   │   └── merchant/
│   │   │       └── page.tsx
│   │   │
│   │   ├── lib/
│   │   │   └── api.ts
│   │   │
│   │   └── types/
│   │       └── commerce.ts
│   │
│   ├── package.json
│   └── next.config.ts
│
├── requirements.txt
└── README.md
```

---

# Running locally

## Backend

Create the Python environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
cd backend
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

Merchant interface:

```text
http://localhost:3000/merchant
```

The frontend expects:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

---

# Tests

Run:

```bash
cd backend
python -m pytest
```

Current result:

```text
20 passed
```

The backend tests currently cover:

- keyword retrieval
- semantic retrieval
- hybrid retrieval
- hard commerce constraints
- structured shopping-intent extraction
- price parsing
- category inference
- ambiguity detection
- conversational search
- follow-up refinement
- cheapest-product lookup
- product comparison
- conversational cart selection
- generic JSON catalog conversion
- generic CSV catalog conversion
- Shopify-style catalog conversion
- catalog validation and invalid input handling

---

# Frontend quality checks

Lint:

```bash
cd frontend
npm run lint
```

Production build:

```bash
npm run build
```

The current frontend passes ESLint and the Next.js production build.

---

# Current development status

## Completed

### Foundation

- ecommerce product model
- deterministic demo catalog
- FastAPI backend
- Next.js frontend
- frontend/backend integration

### Search

- TF-IDF retrieval
- semantic retrieval
- hybrid retrieval
- score normalization
- commerce filtering
- configurable ranking weights
- configurable result count

### Shopping intelligence

- natural-language intent parsing
- category recognition
- brand recognition
- price extraction
- attribute extraction
- ambiguity detection
- clarification handling
- shopping context

### Conversational commerce

- follow-up refinement
- cheapest / most expensive queries
- ordinal product references
- structured comparison
- conversational product selection
- add-to-cart actions

### Storefront

- natural-language search
- product cards
- intent display
- match explanations
- product detail drawer
- clarification interface
- conversation interface
- comparison interface
- cart drawer
- quantity management
- responsive layout

### Catalog architecture

- common internal product model
- generic JSON adapter
- generic CSV adapter
- Shopify-style adapter
- runtime catalog replacement
- automatic search-index rebuild
- automatic semantic-embedding rebuild
- demo catalog reset
- source-independent discovery engine

### Merchant tools

- catalog overview
- catalog statistics
- catalog upload
- source selection
- search configuration
- recommendation limit
- retrieval weighting
- inventory visibility configuration

---

# Remaining work

The functional product is now largely complete.

The final development stage focuses on delivery and portfolio quality.

## Day 8

Planned final work:

```text
Docker
Production environment configuration
Deployment
Final error handling
UI polish
Architecture documentation
Screenshots
Demo recording
GitHub presentation
Portfolio case study
Final README polish
```

After this stage, feature development for Project 1 stops and the project moves into portfolio/demo mode.

---

# Technology

## Backend

```text
Python 3.12
FastAPI
Pydantic
scikit-learn
sentence-transformers
NumPy
pytest
```

## Frontend

```text
Next.js
React
TypeScript
CSS
```

## AI and retrieval

```text
TF-IDF
Sentence embeddings
Cosine similarity
Hybrid retrieval
Structured intent extraction
Constraint-aware filtering
Conversational state
```

## Architecture

```text
Catalog adapters
Runtime dependency rebuilding
REST APIs
Shared internal product model
Merchant configuration
Frontend/backend separation
```

---

# Design principles

## Platform independence

Search and conversational logic depend on the common product model rather than Shopify-specific structures.

## AI where useful, deterministic logic where safer

Semantic retrieval handles fuzzy meaning.

Structured logic handles:

```text
price limits
inventory
product attributes
cart selection
comparisons
ordinal references
```

## Relevance does not override commerce requirements

High semantic similarity cannot bypass explicit shopper constraints.

## External data should not require search-engine rewrites

Adapters transform catalog data into the common model.

The retrieval system remains unchanged.

## Runtime configuration should not require deployment

Catalogs and ranking settings can be changed while the application is running.

---

# Current limitations

This is currently a portfolio/demo application rather than a production commerce platform.

Not yet implemented:

- persistent database
- authentication
- merchant accounts
- production checkout
- persistent server-side cart
- live Shopify Admin or Storefront API authentication
- webhook synchronization
- background catalog indexing jobs
- distributed/vector search infrastructure
- production monitoring

Those concerns are intentionally outside the scope of the initial portfolio project.

---

# Project goal

This project demonstrates how AI retrieval, natural-language understanding, deterministic commerce rules, catalog integrations and a complete frontend experience can work together inside an ecommerce product.

The application combines:

```text
Natural-language understanding
+
keyword retrieval
+
semantic retrieval
+
commerce constraints
+
conversation context
+
catalog adapters
+
runtime configuration
+
merchant tooling
+
storefront experience
```

The result is not tied to a single ecommerce platform and can serve as a foundation for product discovery systems across different commerce stacks.