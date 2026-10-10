export type ProductVariant = {
    id: string;
    sku: string;
    title: string;
    price: number;
    available: boolean;
    options: Record<string, string>;
  };
  
  export type Product = {
    id: string;
    title: string;
    description: string;
    category: string;
    brand: string;
    price: number;
    currency: string;
    tags: string[];
    attributes: Record<string, string | number | boolean>;
    inventory: number;
    variants: ProductVariant[];
  };
  
  export type ShoppingIntent = {
    category: string | null;
    brand: string | null;
    min_price: number | null;
    max_price: number | null;
    color: string | null;
    waterproof: boolean | null;
    lightweight: boolean | null;
    in_stock: boolean | null;
    category_candidates: string[];
    needs_clarification: boolean;
    clarification_question: string | null;
  };
  
  export type SearchResult = {
    product: Product;
    score: number;
    keyword_score: number;
    semantic_score: number;
  };
  
  export type CommerceSearchResponse = {
    query: string;
    intent: ShoppingIntent;
    needs_clarification: boolean;
    clarification_question: string | null;
    results_count?: number;
    results: SearchResult[];
  };
  
  export type ConversationContext = {
    original_query: string | null;
    intent: ShoppingIntent | null;
    current_product_ids: string[];
  };
  
  export type ConversationAction =
    | "search"
    | "refine"
    | "answer"
    | "compare"
    | "add_to_cart"
    | "clarify";
  
  export type ConversationResponse = {
    action: ConversationAction;
    message: string;
    context: ConversationContext;
    results?: SearchResult[];
    comparison?: Product[];
    selected_product?: Product | null;
  };
  
  export type CartItem = {
    product: Product;
    quantity: number;
  };
  
  export type ChatMessage = {
    id: string;
    role: "user" | "assistant";
    text: string;
  };

  export type SearchSettings = {
    max_recommendations: number;
    semantic_weight: number;
    keyword_weight: number;
    hide_unavailable: boolean;
  };
  
  export type CatalogStatus = {
    source: string;
    product_count: number;
    products_in_stock: number;
    variant_count: number;
    category_count: number;
    brand_count: number;
    categories: string[];
    brands: string[];
    settings: SearchSettings;
  };
  
  export type CatalogSource =
    | "generic-json"
    | "generic-csv"
    | "shopify";