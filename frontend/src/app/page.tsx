"use client";

import { FormEvent, useState } from "react";

import { searchCommerce } from "@/lib/api";
import type {
  CommerceSearchResponse,
  Product,
  SearchResult,
} from "@/types/commerce";

const exampleQueries = [
  "black waterproof hiking shoes under €120",
  "comfortable gear for carrying things on a weekend mountain trip",
  "something light for walking through wet mountains",
];

const clarificationOptions = [
  {
    label: "Footwear",
    queryAddition: "hiking shoes",
  },
  {
    label: "Jackets",
    queryAddition: "hiking jacket",
  },
  {
    label: "Backpacks",
    queryAddition: "backpack",
  },
  {
    label: "Camping",
    queryAddition: "camping",
  },
];

function formatCategory(category: string) {
  return category
    .split("-")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1)
    )
    .join(" ");
}

function formatAttributeValue(
  value: string | number | boolean
) {
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return String(value);
}

function getMatchReasons(
  result: SearchResult,
  data: CommerceSearchResponse
) {
  const reasons: string[] = [];
  const { product } = result;
  const intent = data.intent;

  if (
    intent.waterproof === true &&
    product.attributes.waterproof === true
  ) {
    reasons.push("Waterproof");
  }

  if (
    intent.lightweight === true &&
    product.attributes.lightweight === true
  ) {
    reasons.push("Lightweight");
  }

  if (
    intent.color &&
    String(product.attributes.color).toLowerCase() ===
      intent.color.toLowerCase()
  ) {
    reasons.push(intent.color);
  }

  if (
    intent.max_price !== null &&
    product.price <= intent.max_price
  ) {
    reasons.push(`Under €${intent.max_price}`);
  }

  if (
    intent.min_price !== null &&
    product.price >= intent.min_price
  ) {
    reasons.push(`Over €${intent.min_price}`);
  }

  if (intent.category === product.category) {
    reasons.push(formatCategory(product.category));
  }

  return reasons.slice(0, 4);
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [data, setData] =
    useState<CommerceSearchResponse | null>(null);
  const [selectedProduct, setSelectedProduct] =
    useState<Product | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runSearch(searchQuery: string) {
    const trimmed = searchQuery.trim();

    if (!trimmed) {
      return;
    }

    setQuery(trimmed);
    setLoading(true);
    setError("");
    setSelectedProduct(null);

    try {
      const response = await searchCommerce(trimmed);
      setData(response);
    } catch {
      setError(
        "Search is unavailable right now. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    await runSearch(query);
  }

  async function handleClarification(
    addition: string
  ) {
    await runSearch(`${query} ${addition}`);
  }

  return (
    <main>
      <section className="hero">
        <div className="heroContent">
          <div className="eyebrow">
            AI COMMERCE DISCOVERY
          </div>

          <h1>
            Find the right product by describing what
            you actually need.
          </h1>

          <p className="heroDescription">
            Search by use case, price, attributes and
            shopping intent instead of navigating endless
            filters.
          </p>

          <form
            className="searchBox"
            onSubmit={handleSubmit}
          >
            <input
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="e.g. black waterproof hiking shoes under €120"
              aria-label="Search products"
            />

            <button
              type="submit"
              disabled={loading}
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </form>

          <div className="examples">
            <span>Try:</span>

            {exampleQueries.map((example) => (
              <button
                key={example}
                onClick={() => runSearch(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="content">
        {error && (
          <div className="message errorMessage">
            {error}
          </div>
        )}

        {loading && (
          <div className="loadingGrid">
            {Array.from({ length: 3 }).map(
              (_, index) => (
                <div
                  className="skeleton"
                  key={index}
                />
              )
            )}
          </div>
        )}

        {!loading &&
          data?.needs_clarification && (
            <div className="clarification">
              <span className="sectionLabel">
                ONE MORE DETAIL
              </span>

              <h2>
                {data.clarification_question}
              </h2>

              <p>
                Your request contains useful shopping
                preferences, but the product type is still
                ambiguous.
              </p>

              <div className="clarificationButtons">
                {clarificationOptions.map(
                  (option) => (
                    <button
                      key={option.label}
                      onClick={() =>
                        handleClarification(
                          option.queryAddition
                        )
                      }
                    >
                      {option.label}
                    </button>
                  )
                )}
              </div>
            </div>
          )}

        {!loading &&
          data &&
          !data.needs_clarification && (
            <>
              <div className="resultsHeader">
                <div>
                  <span className="sectionLabel">
                    PRODUCT DISCOVERY
                  </span>

                  <h2>
                    {data.results.length > 0
                      ? `${data.results.length} matching products`
                      : "No exact matches"}
                  </h2>

                  <p>
                    Results are ranked by relevance after
                    applying your shopping constraints.
                  </p>
                </div>

                <IntentSummary data={data} />
              </div>

              {data.results.length === 0 ? (
                <div className="message emptyMessage">
                  No products satisfy all of those
                  requirements. Try changing one of the
                  constraints rather than receiving an
                  invalid recommendation.
                </div>
              ) : (
                <div className="productGrid">
                  {data.results.map((result) => (
                    <ProductCard
                      key={result.product.id}
                      result={result}
                      data={data}
                      onView={() =>
                        setSelectedProduct(
                          result.product
                        )
                      }
                    />
                  ))}
                </div>
              )}
            </>
          )}

        {!data && !loading && !error && (
          <div className="introPanel">
            <div>
              <span className="sectionLabel">
                HOW IT WORKS
              </span>
              <h2>
                Shopping intent, not just keywords.
              </h2>
            </div>

            <div className="featureGrid">
              <article>
                <strong>01</strong>
                <h3>Understand</h3>
                <p>
                  Detect category, price and product
                  attributes from natural language.
                </p>
              </article>

              <article>
                <strong>02</strong>
                <h3>Retrieve</h3>
                <p>
                  Combine lexical and semantic relevance
                  for stronger product discovery.
                </p>
              </article>

              <article>
                <strong>03</strong>
                <h3>Enforce</h3>
                <p>
                  Respect hard commerce requirements
                  instead of recommending invalid products.
                </p>
              </article>
            </div>
          </div>
        )}
      </section>

      {selectedProduct && (
        <ProductDrawer
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}
    </main>
  );
}

function IntentSummary({
  data,
}: {
  data: CommerceSearchResponse;
}) {
  const intentItems = [
    data.intent.category
      ? formatCategory(data.intent.category)
      : null,
    data.intent.brand,
    data.intent.color,
    data.intent.waterproof === true
      ? "Waterproof"
      : null,
    data.intent.lightweight === true
      ? "Lightweight"
      : null,
    data.intent.max_price !== null
      ? `≤ €${data.intent.max_price}`
      : null,
    data.intent.min_price !== null
      ? `≥ €${data.intent.min_price}`
      : null,
  ].filter(Boolean);

  if (intentItems.length === 0) {
    return null;
  }

  return (
    <div className="intentSummary">
      <span>Understood</span>

      <div>
        {intentItems.map((item) => (
          <span
            className="intentChip"
            key={item}
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function ProductCard({
  result,
  data,
  onView,
}: {
  result: SearchResult;
  data: CommerceSearchResponse;
  onView: () => void;
}) {
  const product = result.product;
  const reasons = getMatchReasons(result, data);

  return (
    <article className="productCard">
      <div className="productVisual">
        <span>{product.brand}</span>

        <strong>
          {formatCategory(product.category)}
        </strong>
      </div>

      <div className="productBody">
        <div className="productMeta">
          <span>{product.brand}</span>

          <span>
            {product.inventory > 0
              ? `${product.inventory} in stock`
              : "Out of stock"}
          </span>
        </div>

        <h3>{product.title}</h3>

        <p className="productDescription">
          {product.description}
        </p>

        {reasons.length > 0 && (
          <div className="matchReasons">
            {reasons.map((reason) => (
              <span key={reason}>
                ✓ {reason}
              </span>
            ))}
          </div>
        )}

        <div className="productFooter">
          <strong>
            {new Intl.NumberFormat("en-DE", {
              style: "currency",
              currency: product.currency,
            }).format(product.price)}
          </strong>

          <button onClick={onView}>
            View details
          </button>
        </div>
      </div>
    </article>
  );
}

function ProductDrawer({
  product,
  onClose,
}: {
  product: Product;
  onClose: () => void;
}) {
  return (
    <div
      className="drawerBackdrop"
      onClick={onClose}
    >
      <aside
        className="drawer"
        onClick={(event) =>
          event.stopPropagation()
        }
      >
        <button
          className="closeButton"
          onClick={onClose}
          aria-label="Close product details"
        >
          ×
        </button>

        <span className="sectionLabel">
          {product.brand}
        </span>

        <h2>{product.title}</h2>

        <strong className="drawerPrice">
          {new Intl.NumberFormat("en-DE", {
            style: "currency",
            currency: product.currency,
          }).format(product.price)}
        </strong>

        <p>{product.description}</p>

        <div className="detailSection">
          <h3>Product details</h3>

          {Object.entries(product.attributes).map(
            ([key, value]) => (
              <div
                className="detailRow"
                key={key}
              >
                <span>
                  {key
                    .replaceAll("_", " ")
                    .replace(/\b\w/g, (char) =>
                      char.toUpperCase()
                    )}
                </span>

                <strong>
                  {formatAttributeValue(value)}
                </strong>
              </div>
            )
          )}

          <div className="detailRow">
            <span>Inventory</span>
            <strong>{product.inventory}</strong>
          </div>

          <div className="detailRow">
            <span>Category</span>
            <strong>
              {formatCategory(product.category)}
            </strong>
          </div>
        </div>

        <button
          className="primaryAction"
          disabled={product.inventory <= 0}
        >
          {product.inventory > 0
            ? "Add to cart"
            : "Out of stock"}
        </button>
      </aside>
    </div>
  );
}