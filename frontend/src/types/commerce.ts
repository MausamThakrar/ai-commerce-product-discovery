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