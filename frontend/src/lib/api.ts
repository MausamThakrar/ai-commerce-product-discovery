import type {
    CommerceSearchResponse,
    ConversationContext,
    ConversationResponse,
    CatalogSource,
    CatalogStatus,
    SearchSettings,
  } from "@/types/commerce";
  
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://127.0.0.1:8000";
  
  export async function searchCommerce(
    query: string,
    topK = 6
  ): Promise<CommerceSearchResponse> {
    const params = new URLSearchParams({
      q: query,
      top_k: String(topK),
    });
  
    const response = await fetch(
      `${API_BASE_URL}/search/commerce?${params.toString()}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      }
    );
  
    if (!response.ok) {
      throw new Error(
        `Search request failed with status ${response.status}`
      );
    }
  
    return response.json();
  }
  
  export async function sendConversationMessage(
    message: string,
    context: ConversationContext,
    topK = 6
  ): Promise<ConversationResponse> {
    const response = await fetch(
      `${API_BASE_URL}/conversation`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          message,
          context,
          top_k: topK,
        }),
      }
    );
  
    if (!response.ok) {
      throw new Error(
        `Conversation request failed with status ${response.status}`
      );
    }
  
    return response.json();
  }
  export async function getCatalogStatus(): Promise<CatalogStatus> {
    const response = await fetch(
      `${API_BASE_URL}/merchant/catalog`
    );
  
    if (!response.ok) {
      throw new Error(
        "Failed to load catalog status"
      );
    }
  
    return response.json();
  }
  
  
  export async function importCatalog(
    source: CatalogSource,
    fileText: string
  ): Promise<CatalogStatus> {
    let body;
  
    if (source === "generic-csv") {
      body = {
        source,
        csv_text: fileText,
      };
    } else {
      let payload;
  
      try {
        payload = JSON.parse(
          fileText
        );
      } catch {
        throw new Error(
          "The selected file is not valid JSON."
        );
      }
  
      body = {
        source,
        payload,
      };
    }
  
    const response = await fetch(
      `${API_BASE_URL}/merchant/catalog/import`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(body),
      }
    );
  
    const result = await response.json();
  
    if (!response.ok) {
      throw new Error(
        result.detail ??
          "Catalog import failed"
      );
    }
  
    return result.catalog;
  }
  
  
  export async function resetCatalog(): Promise<CatalogStatus> {
    const response = await fetch(
      `${API_BASE_URL}/merchant/catalog/reset`,
      {
        method: "POST",
      }
    );
  
    const result = await response.json();
  
    if (!response.ok) {
      throw new Error(
        result.detail ??
          "Catalog reset failed"
      );
    }
  
    return result.catalog;
  }
  
  
  export async function updateSearchSettings(
    settings: SearchSettings
  ): Promise<SearchSettings> {
    const response = await fetch(
      `${API_BASE_URL}/merchant/settings`,
      {
        method: "PUT",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(
          settings
        ),
      }
    );
  
    const result = await response.json();
  
    if (!response.ok) {
      throw new Error(
        result.detail ??
          "Settings update failed"
      );
    }
  
    return result.settings;
  }