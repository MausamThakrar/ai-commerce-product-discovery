"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  searchCommerce,
  sendConversationMessage,
} from "@/lib/api";

import type {
  CartItem,
  ChatMessage,
  CommerceSearchResponse,
  ConversationContext,
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
        word.charAt(0).toUpperCase() +
        word.slice(1)
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


function formatAttributeLabel(key: string) {
  return key
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


function formatPrice(product: Product) {
  return new Intl.NumberFormat(
    "en-DE",
    {
      style: "currency",
      currency: product.currency,
    }
  ).format(product.price);
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
    String(
      product.attributes.color
    ).toLowerCase() ===
      intent.color.toLowerCase()
  ) {
    reasons.push(intent.color);
  }

  if (
    intent.max_price !== null &&
    product.price <= intent.max_price
  ) {
    reasons.push(
      `Under €${intent.max_price}`
    );
  }

  if (
    intent.min_price !== null &&
    product.price >= intent.min_price
  ) {
    reasons.push(
      `Over €${intent.min_price}`
    );
  }

  if (
    intent.category === product.category
  ) {
    reasons.push(
      formatCategory(product.category)
    );
  }

  return reasons.slice(0, 4);
}


export default function Home() {
  const [query, setQuery] = useState("");

  const [data, setData] =
    useState<CommerceSearchResponse | null>(
      null
    );

  const [
    selectedProduct,
    setSelectedProduct,
  ] = useState<Product | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [
    conversationContext,
    setConversationContext,
  ] =
    useState<ConversationContext>({
      original_query: null,
      intent: null,
      current_product_ids: [],
    });

  const [chatInput, setChatInput] =
    useState("");

  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [comparison, setComparison] =
    useState<Product[]>([]);

  const [cart, setCart] =
    useState<CartItem[]>([]);

  const [cartOpen, setCartOpen] =
    useState(false);

  const [
    conversationLoading,
    setConversationLoading,
  ] = useState(false);


  const cartQuantity = cart.reduce(
    (total, item) =>
      total + item.quantity,
    0
  );


  const cartTotal = cart.reduce(
    (total, item) =>
      total +
      item.product.price *
        item.quantity,
    0
  );


  function addToCart(product: Product) {
    setCart((current) => {
      const existing =
        current.find(
          (item) =>
            item.product.id ===
            product.id
        );

      if (existing) {
        return current.map(
          (item) =>
            item.product.id ===
            product.id
              ? {
                  ...item,
                  quantity:
                    item.quantity + 1,
                }
              : item
        );
      }

      return [
        ...current,
        {
          product,
          quantity: 1,
        },
      ];
    });
  }


  function changeQuantity(
    productId: string,
    amount: number
  ) {
    setCart((current) =>
      current
        .map((item) =>
          item.product.id === productId
            ? {
                ...item,
                quantity:
                  item.quantity +
                  amount,
              }
            : item
        )
        .filter(
          (item) =>
            item.quantity > 0
        )
    );
  }


  function removeFromCart(
    productId: string
  ) {
    setCart((current) =>
      current.filter(
        (item) =>
          item.product.id !== productId
      )
    );
  }


  async function runSearch(
    searchQuery: string
  ) {
    const trimmed =
      searchQuery.trim();

    if (!trimmed) {
      return;
    }

    setQuery(trimmed);
    setLoading(true);
    setError("");
    setSelectedProduct(null);
    setComparison([]);

    try {
      const response =
        await searchCommerce(trimmed);

      setData(response);

      setConversationContext({
        original_query: trimmed,
        intent: response.intent,
        current_product_ids:
          response.results.map(
            (result) =>
              result.product.id
          ),
      });

      setMessages([
        {
          id: crypto.randomUUID(),
          role: "user",
          text: trimmed,
        },
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text:
            response.needs_clarification
              ? response
                  .clarification_question ??
                "I need more information."
              : `I found ${response.results.length} matching products.`,
        },
      ]);
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
    await runSearch(
      `${query} ${addition}`
    );
  }


  async function sendChatMessage(
    rawMessage: string
  ) {
    const message =
      rawMessage.trim();

    if (!message) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      text: message,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setChatInput("");
    setConversationLoading(true);

    try {
      const response =
        await sendConversationMessage(
          message,
          conversationContext
        );

      setConversationContext(
        response.context
      );

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: response.message,
        },
      ]);

      if (
        response.action === "search" ||
        response.action === "refine"
      ) {
        if (
          response.context.intent
        ) {
          setData({
            query:
              response.context
                .original_query ??
              message,

            intent:
              response.context.intent,

            needs_clarification:
              false,

            clarification_question:
              null,

            results_count:
              response.results
                ?.length ?? 0,

            results:
              response.results ?? [],
          });
        }

        setComparison([]);
      }

      if (
        response.action === "compare"
      ) {
        setComparison(
          response.comparison ?? []
        );
      }

      if (
        response.action ===
          "add_to_cart" &&
        response.selected_product
      ) {
        addToCart(
          response.selected_product
        );
      }

      if (
        response.action === "clarify" &&
        response.context.intent
      ) {
        setData({
          query: message,
          intent:
            response.context.intent,
          needs_clarification: true,
          clarification_question:
            response.message,
          results: [],
        });
      }
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text:
            "I couldn't process that request.",
        },
      ]);
    } finally {
      setConversationLoading(false);
    }
  }


  async function handleChatSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    await sendChatMessage(
      chatInput
    );
  }


  return (
    <main>
      <section className="hero">
        <div className="heroContent">
          <div className="eyebrow">
            AI COMMERCE DISCOVERY
          </div>

          <h1>
            Find the right product by
            describing what you actually
            need.
          </h1>

          <p className="heroDescription">
            Search by use case, price,
            attributes and shopping intent
            instead of navigating endless
            filters.
          </p>

          <form
            className="searchBox"
            onSubmit={handleSubmit}
          >
            <input
              value={query}
              onChange={(event) =>
                setQuery(
                  event.target.value
                )
              }
              placeholder="e.g. black waterproof hiking shoes under €120"
              aria-label="Search products"
            />

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Searching..."
                : "Search"}
            </button>
          </form>

          <div className="examples">
            <span>Try:</span>

            {exampleQueries.map(
              (example) => (
                <button
                  key={example}
                  onClick={() =>
                    runSearch(example)
                  }
                >
                  {example}
                </button>
              )
            )}
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
            {Array.from({
              length: 3,
            }).map((_, index) => (
              <div
                className="skeleton"
                key={index}
              />
            ))}
          </div>
        )}


        {!loading &&
          data?.needs_clarification && (
            <div className="clarification">
              <span className="sectionLabel">
                ONE MORE DETAIL
              </span>

              <h2>
                {
                  data.clarification_question
                }
              </h2>

              <p>
                Your request contains useful
                shopping preferences, but the
                product type is still
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
                    {data.results.length >
                    0
                      ? `${data.results.length} matching products`
                      : "No exact matches"}
                  </h2>

                  <p>
                    Results are ranked by
                    relevance after applying
                    your shopping constraints.
                  </p>
                </div>

                <IntentSummary
                  data={data}
                />
              </div>

              {data.results.length ===
              0 ? (
                <div className="message emptyMessage">
                  No products satisfy all of
                  those requirements. Try
                  changing one of the
                  constraints rather than
                  receiving an invalid
                  recommendation.
                </div>
              ) : (
                <div className="productGrid">
                  {data.results.map(
                    (result) => (
                      <ProductCard
                        key={
                          result.product.id
                        }
                        result={result}
                        data={data}
                        onView={() =>
                          setSelectedProduct(
                            result.product
                          )
                        }
                      />
                    )
                  )}
                </div>
              )}

              <section className="conversationPanel">
                <div className="conversationHeader">
                  <div>
                    <span className="sectionLabel">
                      CONTINUE SHOPPING
                    </span>

                    <h2>
                      Refine, compare or choose
                      a product
                    </h2>
                  </div>

                  <button
                    className="cartButton"
                    onClick={() =>
                      setCartOpen(true)
                    }
                  >
                    Cart ({cartQuantity})
                  </button>
                </div>

                <div className="chatMessages">
                  {messages.map(
                    (message) => (
                      <div
                        key={message.id}
                        className={`chatMessage ${message.role}`}
                      >
                        {message.text}
                      </div>
                    )
                  )}
                </div>

                <form
                  className="chatForm"
                  onSubmit={
                    handleChatSubmit
                  }
                >
                  <input
                    value={chatInput}
                    onChange={(event) =>
                      setChatInput(
                        event.target.value
                      )
                    }
                    placeholder='Try "only black ones" or "compare the first two"'
                  />

                  <button
                    type="submit"
                    disabled={
                      conversationLoading
                    }
                  >
                    {conversationLoading
                      ? "Thinking..."
                      : "Send"}
                  </button>
                </form>

                <div className="conversationSuggestions">
                  <button
                    onClick={() =>
                      sendChatMessage(
                        "which is cheapest?"
                      )
                    }
                    disabled={
                      conversationLoading
                    }
                  >
                    Which is cheapest?
                  </button>

                  <button
                    onClick={() =>
                      sendChatMessage(
                        "compare the first two"
                      )
                    }
                    disabled={
                      conversationLoading
                    }
                  >
                    Compare first two
                  </button>

                  <button
                    onClick={() =>
                      sendChatMessage(
                        "only black ones"
                      )
                    }
                    disabled={
                      conversationLoading
                    }
                  >
                    Only black
                  </button>

                  <button
                    onClick={() =>
                      sendChatMessage(
                        "add the cheapest one to cart"
                      )
                    }
                    disabled={
                      conversationLoading
                    }
                  >
                    Add cheapest to cart
                  </button>
                </div>
              </section>

              {comparison.length >= 2 && (
                <section className="comparisonPanel">
                  <span className="sectionLabel">
                    PRODUCT COMPARISON
                  </span>

                  <h2>
                    Compare products
                  </h2>

                  <div className="comparisonGrid">
                    {comparison.map(
                      (product) => (
                        <article
                          key={product.id}
                          className="comparisonCard"
                        >
                          <h3>
                            {
                              product.title
                            }
                          </h3>

                          <strong className="comparisonPrice">
                            {formatPrice(
                              product
                            )}
                          </strong>

                          <div className="comparisonDetails">
                            <span>
                              Brand
                              <strong>
                                {
                                  product.brand
                                }
                              </strong>
                            </span>

                            <span>
                              Category
                              <strong>
                                {formatCategory(
                                  product.category
                                )}
                              </strong>
                            </span>

                            <span>
                              Stock
                              <strong>
                                {
                                  product.inventory
                                }
                              </strong>
                            </span>

                            {Object.entries(
                              product.attributes
                            ).map(
                              ([
                                key,
                                value,
                              ]) => (
                                <span
                                  key={
                                    key
                                  }
                                >
                                  {formatAttributeLabel(
                                    key
                                  )}

                                  <strong>
                                    {formatAttributeValue(
                                      value
                                    )}
                                  </strong>
                                </span>
                              )
                            )}
                          </div>
                        </article>
                      )
                    )}
                  </div>
                </section>
              )}
            </>
          )}


        {!data &&
          !loading &&
          !error && (
            <div className="introPanel">
              <div>
                <span className="sectionLabel">
                  HOW IT WORKS
                </span>

                <h2>
                  Shopping intent, not just
                  keywords.
                </h2>
              </div>

              <div className="featureGrid">
                <article>
                  <strong>01</strong>
                  <h3>Understand</h3>
                  <p>
                    Detect category, price and
                    product attributes from
                    natural language.
                  </p>
                </article>

                <article>
                  <strong>02</strong>
                  <h3>Retrieve</h3>
                  <p>
                    Combine lexical and
                    semantic relevance for
                    stronger product discovery.
                  </p>
                </article>

                <article>
                  <strong>03</strong>
                  <h3>Enforce</h3>
                  <p>
                    Respect hard commerce
                    requirements instead of
                    recommending invalid
                    products.
                  </p>
                </article>
              </div>
            </div>
          )}
      </section>


      {selectedProduct && (
        <ProductDrawer
          product={selectedProduct}
          onClose={() =>
            setSelectedProduct(null)
          }
          onAddToCart={() => {
            addToCart(
              selectedProduct
            );

            setSelectedProduct(null);
          }}
        />
      )}


      {cartOpen && (
        <CartDrawer
          cart={cart}
          total={cartTotal}
          onClose={() =>
            setCartOpen(false)
          }
          onIncrease={(productId) =>
            changeQuantity(
              productId,
              1
            )
          }
          onDecrease={(productId) =>
            changeQuantity(
              productId,
              -1
            )
          }
          onRemove={removeFromCart}
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
      ? formatCategory(
          data.intent.category
        )
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

  const reasons =
    getMatchReasons(
      result,
      data
    );

  return (
    <article className="productCard">
      <div className="productVisual">
        <span>
          {product.brand}
        </span>

        <strong>
          {formatCategory(
            product.category
          )}
        </strong>
      </div>

      <div className="productBody">
        <div className="productMeta">
          <span>
            {product.brand}
          </span>

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
            {reasons.map(
              (reason) => (
                <span key={reason}>
                  ✓ {reason}
                </span>
              )
            )}
          </div>
        )}

        <div className="productFooter">
          <strong>
            {formatPrice(product)}
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
  onAddToCart,
}: {
  product: Product;
  onClose: () => void;
  onAddToCart: () => void;
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
          {formatPrice(product)}
        </strong>

        <p>
          {product.description}
        </p>

        <div className="detailSection">
          <h3>Product details</h3>

          {Object.entries(
            product.attributes
          ).map(([key, value]) => (
            <div
              className="detailRow"
              key={key}
            >
              <span>
                {formatAttributeLabel(
                  key
                )}
              </span>

              <strong>
                {formatAttributeValue(
                  value
                )}
              </strong>
            </div>
          ))}

          <div className="detailRow">
            <span>
              Inventory
            </span>

            <strong>
              {product.inventory}
            </strong>
          </div>

          <div className="detailRow">
            <span>
              Category
            </span>

            <strong>
              {formatCategory(
                product.category
              )}
            </strong>
          </div>
        </div>

        <button
          className="primaryAction"
          disabled={
            product.inventory <= 0
          }
          onClick={
            onAddToCart
          }
        >
          {product.inventory > 0
            ? "Add to cart"
            : "Out of stock"}
        </button>
      </aside>
    </div>
  );
}


function CartDrawer({
  cart,
  total,
  onClose,
  onIncrease,
  onDecrease,
  onRemove,
}: {
  cart: CartItem[];
  total: number;
  onClose: () => void;
  onIncrease: (
    productId: string
  ) => void;
  onDecrease: (
    productId: string
  ) => void;
  onRemove: (
    productId: string
  ) => void;
}) {
  return (
    <div
      className="drawerBackdrop"
      onClick={onClose}
    >
      <aside
        className="drawer cartDrawer"
        onClick={(event) =>
          event.stopPropagation()
        }
      >
        <button
          className="closeButton"
          onClick={onClose}
          aria-label="Close cart"
        >
          ×
        </button>

        <span className="sectionLabel">
          YOUR CART
        </span>

        <h2>
        {cart.length === 0
          ? "Your cart is empty"
          : `${cart.length} ${
              cart.length === 1 ? "product" : "products"
            }`}
        </h2>

        {cart.map((item) => (
          <div
            className="cartItem"
            key={item.product.id}
          >
            <div className="cartItemInfo">
              <strong>
                {item.product.title}
              </strong>

              <span>
                {formatPrice(
                  item.product
                )}
              </span>

              <div className="quantityControls">
                <button
                  onClick={() =>
                    onDecrease(
                      item.product.id
                    )
                  }
                >
                  −
                </button>

                <span>
                  {item.quantity}
                </span>

                <button
                  onClick={() =>
                    onIncrease(
                      item.product.id
                    )
                  }
                >
                  +
                </button>
              </div>

              <button
                className="removeButton"
                onClick={() =>
                  onRemove(
                    item.product.id
                  )
                }
              >
                Remove
              </button>
            </div>

            <strong>
              {new Intl.NumberFormat(
                "en-DE",
                {
                  style: "currency",
                  currency:
                    item.product
                      .currency,
                }
              ).format(
                item.product.price *
                  item.quantity
              )}
            </strong>
          </div>
        ))}

        {cart.length > 0 && (
          <div className="cartTotal">
            <span>Total</span>

            <strong>
              {new Intl.NumberFormat(
                "en-DE",
                {
                  style: "currency",
                  currency: "EUR",
                }
              ).format(total)}
            </strong>
          </div>
        )}
      </aside>
    </div>
  );
}