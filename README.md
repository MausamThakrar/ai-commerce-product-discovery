# AI Commerce Product Discovery

An ecommerce product discovery project exploring keyword search, semantic retrieval, hybrid search, and AI-assisted product search.

## Current Status

Day 2 complete.

Current capabilities:

- Structured ecommerce product catalog
- 120 synthetic products
- FastAPI backend
- TF-IDF keyword search
- Semantic search using sentence embeddings
- Ranked product retrieval
- Keyword vs semantic search comparison
- Automated tests

## Tech Stack

- Python 3.12
- FastAPI
- Pydantic
- scikit-learn
- sentence-transformers
- pytest

## API Endpoints

- `GET /health`
- `GET /products`
- `GET /search`
- `GET /search/semantic`

## Example Search

```text
something light for walking through wet mountains
```

## Search Approaches

### Keyword Search

The baseline search uses TF-IDF to rank products based on lexical similarity between the shopper query and product content.

This approach works well when the query contains words that also appear directly in product titles, descriptions, categories, or tags.

### Semantic Search

Semantic search uses sentence embeddings to retrieve products based on meaning rather than exact keyword overlap.

For example, for the query:

```text
something light for walking through wet mountains
```

semantic search can associate:

- `light` with `lightweight`
- `wet` with `waterproof` and `weather-resistant`
- `mountains` with `hiking` and `mountain trekking`

This allows relevant products to be retrieved even when the shopper uses different wording from the product catalog.

## Keyword vs Semantic Search

The project currently supports both keyword and semantic retrieval so their behavior can be compared directly.

Keyword search tends to perform well when the shopper uses explicit catalog terminology.

Semantic search is better at understanding natural-language intent and related concepts.

The initial comparison also exposes an important limitation of semantic similarity alone.

For example, a query about staying dry while hiking may retrieve waterproof backpacks because they are semantically related to the query, even if the shopper intended to find clothing or footwear.

This shows why ecommerce search needs more than semantic similarity.

The next step is to combine semantic relevance with keyword ranking and structured product constraints.

## Current Limitations

The current search system does not yet enforce structured ecommerce requirements such as:

- category
- minimum and maximum price
- brand
- color
- availability
- waterproof status
- lightweight status

It also does not yet extract these requirements automatically from natural-language queries.

## Roadmap

Next steps:

- Hybrid keyword + semantic search
- Structured ecommerce filtering
- Natural-language query understanding
- Search evaluation
- Frontend interface
- AI-generated product explanations

## Testing

Run the test suite from the `backend` directory:

```bash
python -m pytest
```

Current test status:

```text
4 passed
```