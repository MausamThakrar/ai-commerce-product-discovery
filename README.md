# AI Commerce Product Discovery

A conversational AI-powered product discovery and shopping experience for ecommerce.

The application understands natural-language shopping requests, combines keyword and semantic retrieval, enforces hard commerce constraints, supports follow-up refinement and product comparison, and allows shoppers to add recommended products to a cart.

The core discovery engine is intentionally ecommerce-platform independent. Platform-specific catalog integrations can be added through adapters.

---

## Current product experience

A shopper can start with:

```text
waterproof hiking shoes under €200
```

The system understands the request, retrieves relevant products and applies the requested commerce constraints.

The shopper can then continue naturally:

```text
only black ones
```

The existing search is refined rather than restarted.

Then:

```text
which is cheapest?
```

The assistant evaluates the current result set.

Then:

```text
compare the first two
```

A structured product comparison is displayed.

And:

```text
add the cheapest one to cart
```

The selected product is added to the cart.

This allows product discovery to behave more like a guided shopping interaction than a traditional keyword search page.

---

## Current capabilities

### Product discovery

- Natural-language product search
- TF-IDF keyword retrieval
- Semantic retrieval using sentence-transformer embeddings
- Hybrid keyword + semantic ranking
- Normalized retrieval scores
- Commerce-aware result filtering

### Commerce constraints

The system can enforce:

- category
- brand
- minimum price
- maximum price
- color
- waterproof requirement
- lightweight requirement
- inventory availability

These are treated as hard constraints rather than ranking preferences.

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

A €180 product cannot appear simply because it has a high semantic relevance score.

---

## Shopping intent and clarification

The intent layer extracts structured shopping requirements from natural language.

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

The system can also detect when a request is not specific enough.

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

Instead of returning arbitrary semantically similar products, the system asks for clarification.

```text
What type of product are you looking for:
footwear, a jacket, a backpack, or camping equipment?
```

---

## Conversational shopping

Search state is retained between shopper messages.

A conversation can look like:

```text
Shopper:
waterproof hiking shoes under €200

Assistant:
I found 6 matching products.

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

Supported conversational operations currently include:

- refining previous search constraints
- cheapest product lookup
- most expensive product lookup
- references such as first, second and third product
- comparison of current products
- add-to-cart commands
- continued use of previous shopping intent

Simple ecommerce operations are handled deterministically rather than delegating every action to a language model.

---

## Product comparison

The storefront can compare products from the current recommendation set.

The comparison includes data such as:

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

The comparison is generated from structured catalog data rather than free-form generated text.

---

## Cart

The current frontend includes a client-side shopping cart.

Supported interactions include:

- add product from product details
- add product through conversation
- increase quantity
- decrease quantity
- remove product
- calculate line totals
- calculate cart total

The current cart is intentionally local to the demo application. A commerce-platform cart adapter will be added separately.

---

## Search architecture

```text
                        Shopper
                           |
                           v
                  Next.js Storefront
                           |
              +------------+-------------+
              |                          |
              v                          v
         Search UI                Conversation UI
              |                          |
              +-------------+------------+
                            |
                            v
                         FastAPI
                            |
              +-------------+-------------+
              |                           |
              v                           v
     Commerce Search Service      Conversation Service
              |                           |
              |                    +------+------+
              |                    |             |
              |                 Context       Actions
              |                    |             |
              |                    |       +-----+------+
              |                    |       |     |      |
              |                    |    Refine Compare Cart
              |                    |
              +----------+---------+
                         |
                         v
                  Shopping Intent
                         |
              +----------+----------+
              |                     |
              v                     v
       Ambiguity Detection     Hard Constraints
              |                     |
              +----------+----------+
                         |
                         v
                 Hybrid Retrieval
                 /              \
                v                v
        Keyword Search      Semantic Search
          TF-IDF            Embeddings
                \                /
                 +------+-------+
                        |
                        v
                 Ranked Products
```

---

## Retrieval methods

### Keyword search

The keyword baseline uses TF-IDF with unigram and bigram features.

It is useful when shopper terminology closely matches text in the product catalog.

### Semantic search

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

This allows conceptually related products to be retrieved even when the shopper does not use the exact catalog terminology.

### Hybrid search

Keyword and semantic scores are normalized and combined.

Current weighting:

```text
Semantic: 65%
Keyword:  35%
```

The current weights are application defaults and can be tuned later.

---

## Relevance vs eligibility

A central design principle is the distinction between:

```text
Relevance
```

and:

```text
Eligibility
```

Retrieval scores answer:

> How relevant is this product to the shopper's request?

Commerce constraints answer:

> Is this product allowed to appear at all?

For example:

```text
waterproof hiking shoes under €120
```

requires the product to satisfy the requested category, waterproof requirement and price ceiling before ranking determines the final order.

---

## Frontend

The storefront is built with Next.js and TypeScript.

Current UI functionality includes:

- natural-language search
- example shopping queries
- extracted intent chips
- responsive product cards
- match explanations
- clarification flow
- product detail drawer
- conversational follow-up interface
- structured product comparison
- shopping cart drawer
- quantity management
- loading states
- empty states
- API error handling
- responsive mobile layout

Frontend development URL:

```text
http://localhost:3000
```

---

## API

The backend is built with FastAPI.

API documentation:

```text
http://127.0.0.1:8000/docs
```

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

1. interprets the natural-language request
2. extracts shopping constraints
3. checks whether the product type is sufficiently clear
4. asks for clarification when necessary
5. performs hybrid retrieval
6. enforces hard commerce constraints
7. returns ranked products

### Conversation

```http
POST /conversation
```

Example request:

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
  },
  "top_k": 6
}
```

The conversation service can return actions such as:

```text
search
refine
answer
compare
add_to_cart
clarify
```

---

## Catalog

The current demo catalog contains 120 deterministic synthetic ecommerce products across:

```text
trail-shoes
hiking-jackets
backpacks
camping
```

Products contain:

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

The synthetic catalog provides a reproducible development environment while keeping the discovery engine independent of any single ecommerce platform.

External catalog adapters are planned next.

---

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
│   │   │   ├── intent.py
│   │   │   └── conversation.py
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
│   │   ├── test_intent.py
│   │   └── test_conversation.py
│   │
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
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

## Running locally

### Backend

Create and activate a Python virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

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

### Frontend

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

The frontend expects:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

---

## Tests

Run backend tests:

```bash
cd backend
python -m pytest
```

Current result:

```text
15 passed
```

The backend test suite currently covers:

- keyword retrieval
- semantic retrieval
- hybrid retrieval
- hard commerce constraints
- structured shopping-intent extraction
- price parsing
- category inference
- ambiguity detection
- new conversational searches
- follow-up refinement
- cheapest-product lookup
- product comparison
- conversational cart selection

---

## Frontend quality checks

Lint:

```bash
cd frontend
npm run lint
```

Production build:

```bash
npm run build
```

The current frontend passes both ESLint and the Next.js production build.

---

## Current development status

### Completed

#### Foundation

- ecommerce product data model
- deterministic synthetic catalog
- FastAPI backend
- Next.js frontend
- frontend/backend API integration

#### Search

- keyword retrieval
- semantic retrieval
- hybrid retrieval
- score normalization
- hard ecommerce filtering

#### Shopping intelligence

- natural-language intent parsing
- category recognition
- brand recognition
- price extraction
- attribute extraction
- ambiguity detection
- clarification flow
- shopping context

#### Conversational commerce

- follow-up search refinement
- cheapest / most expensive product queries
- ordinal product references
- structured comparison
- conversational product selection
- add-to-cart commands

#### Storefront

- product cards
- intent display
- product detail drawer
- clarification interface
- conversation interface
- comparison interface
- cart drawer
- quantity management
- responsive layout

---

## Remaining work

### Catalog integrations

Replace the synthetic-only catalog source with a reusable adapter architecture.

Planned sources include:

```text
Generic JSON / CSV
Shopify
```

The core discovery engine should not depend on a single commerce platform.

### Merchant configuration

Add configuration for search and catalog behavior such as:

```text
Maximum recommendations
Inventory behavior
Search weighting
Available catalog
```

### Delivery and portfolio polish

Final project work will include:

```text
Docker
Deployment
Environment configuration
Architecture documentation
Screenshots
Demo recording
Final README polish
Portfolio case study
```

---

## Technology

### Backend

```text
Python 3.12
FastAPI
Pydantic
scikit-learn
sentence-transformers
NumPy
pytest
```

### Frontend

```text
Next.js
React
TypeScript
CSS
```

### AI / retrieval

```text
TF-IDF
Sentence embeddings
Cosine similarity
Hybrid retrieval
Structured intent extraction
Constraint-aware filtering
Conversational state
```

---

## Project goal

This project is being built as a practical AI commerce product rather than a standalone machine-learning experiment.

The objective is to demonstrate how AI retrieval, natural-language understanding and deterministic ecommerce logic can work together inside a complete shopping experience.

The system combines:

```text
AI retrieval
+
commerce rules
+
structured product data
+
conversation context
+
frontend product experience
```

The next stage focuses on making the engine reusable with external ecommerce catalogs and platform adapters.