import type { CommerceSearchResponse } from "@/types/commerce";

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