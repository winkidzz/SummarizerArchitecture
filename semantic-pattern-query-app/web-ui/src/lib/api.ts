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

export interface RetrievalMetrics {
  documents: Array<{
    rank: number;
    tier: number;
    source_type: string;
    document_id: string;
    source_path: string;
    score: number;
    rrf_score?: number;
    similarity_score?: number;
    trust_score?: number;
    url?: string;
    title: string;
    chunk_text: string;
  }>;
  tier_breakdown: {
    tier_1: {
      count: number;
      avg_score: number;
      max_score: number;
      documents: any[];
    };
    tier_2: {
      count: number;
      avg_score: number;
      max_score: number;
      documents: any[];
    };
    tier_3: {
      count: number;
      avg_score: number;
      max_score: number;
      documents: any[];
    };
  };
  decision_path: {
    cache_checked: boolean;
    cache_hit: boolean;
    vector_search_used: boolean;
    bm25_search_used: boolean;
    web_kb_used: boolean;
    web_live_used: boolean;
    rrf_fusion_used: boolean;
    reranking_used: boolean;
  };
  search_parameters: {
    query: string;
    top_k: number;
    embedder_type: string;
    enable_web_search: boolean;
    web_mode: string | null;
  };
}

export interface GenerationReasoning {
  context_selection: {
    total_retrieved: number;
    used_in_prompt: number;
    truncated_docs: number;
    reasoning: string;
  };
  document_ranking: {
    sort_method: string;
    description: string;
  };
  prompt_structure: {
    type: string;
    instructions: string;
    temperature: number;
    max_response_tokens: number;
  };
  citations_found: number;
  model_used: string;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDocument[];
  cache_hit: boolean;
  retrieved_docs: number;
  context_docs_used?: number;
  retrieval_stats?: RetrievalStats;
  retrieval_metrics?: RetrievalMetrics;
  generation_reasoning?: GenerationReasoning;
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
