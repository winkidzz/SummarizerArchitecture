const DEFAULT_API_BASE_URL = "http://localhost:8000";

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string) ?? DEFAULT_API_BASE_URL;

export interface SourceDocument {
  document_id?: string;
  source_path?: string;
  document_type?: string;
  score?: number;
  [key: string]: unknown;
}

export interface RetrievalStats {
  tier_1_results?: number;
  tier_2_results?: number;
  tier_3_results?: number;
  cache_hit?: boolean;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDocument[];
  cache_hit: boolean;
  retrieved_docs: number;
  context_docs_used?: number;
  retrieval_stats?: RetrievalStats;
}

export interface QueryPayload {
  query: string;
  top_k?: number;
  use_cache?: boolean;
  query_embedder_type?: "ollama" | "gemini";
  user_context?: Record<string, unknown>;
  enable_web_search?: boolean;
  web_mode?: "parallel" | "on_low_confidence";
}

export interface SystemStats {
  vector_dimension?: number;
  embedding_models?: Record<string, string>;
  qdrant?: Record<string, unknown>;
  [key: string]: unknown;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(
      (message?.detail as string) ??
        `Request failed with status ${response.status}`
    );
  }
  return (await response.json()) as T;
}

export async function sendQuery(payload: QueryPayload): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<QueryResponse>(response);
}

export async function fetchStats(): Promise<SystemStats> {
  const response = await fetch(`${API_BASE_URL}/stats`);
  return handleResponse<SystemStats>(response);
}

export async function fetchDocumentContent(
  documentPath: string
): Promise<{ content: string; metadata: Record<string, unknown> }> {
  const response = await fetch(
    `${API_BASE_URL}/document/content?path=${encodeURIComponent(documentPath)}`
  );
  return handleResponse<{ content: string; metadata: Record<string, unknown> }>(response);
}

export async function fetchDirectoryContents(
  directoryPath: string
): Promise<{ items: Array<{ name: string; path: string; type: "file" | "directory"; extension?: string }> }> {
  const response = await fetch(
    `${API_BASE_URL}/directory/contents?path=${encodeURIComponent(directoryPath)}`
  );
  return handleResponse<{ items: Array<{ name: string; path: string; type: "file" | "directory"; extension?: string }> }>(response);
}
