import { useState } from "react";

interface RetrievalMetrics {
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

interface GenerationReasoning {
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

interface SearchMetricsProps {
  retrieval_metrics?: RetrievalMetrics;
  generation_reasoning?: GenerationReasoning;
}

const SearchMetrics = ({ retrieval_metrics, generation_reasoning }: SearchMetricsProps) => {
  const [expandedSection, setExpandedSection] = useState<string | null>("decision-path");
  const [expandedTier, setExpandedTier] = useState<string | null>(null);

  if (!retrieval_metrics && !generation_reasoning) {
    return null;
  }

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const toggleTier = (tier: string) => {
    setExpandedTier(expandedTier === tier ? null : tier);
  };

  const getTierLabel = (tier: number) => {
    switch (tier) {
      case 1:
        return "Tier 1: Pattern Library";
      case 2:
        return "Tier 2: Web Knowledge Base";
      case 3:
        return "Tier 3: Live Web Search";
      default:
        return `Tier ${tier}`;
    }
  };

  const getTierColor = (tier: number) => {
    switch (tier) {
      case 1:
        return "#4CAF50";
      case 2:
        return "#2196F3";
      case 3:
        return "#FF9800";
      default:
        return "#999";
    }
  };

  const formatScore = (score: number | undefined) => {
    if (score === undefined) return "N/A";
    return score.toFixed(4);
  };

  return (
    <section className="panel search-metrics-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Search Metrics</p>
          <h2>🔍 Retrieval & Generation Analysis</h2>
        </div>
      </div>

      <div style={{ padding: "16px" }}>
        {/* Decision Path */}
        {retrieval_metrics?.decision_path && (
          <div className="metrics-section">
            <div
              className="metrics-section-header"
              onClick={() => toggleSection("decision-path")}
              style={{ cursor: "pointer", padding: "12px", backgroundColor: "#f5f5f5", borderRadius: "4px", marginBottom: "8px" }}
            >
              <strong>🛤️ Decision Path & Search Strategy</strong>
              <span style={{ float: "right" }}>{expandedSection === "decision-path" ? "▼" : "▶"}</span>
            </div>
            {expandedSection === "decision-path" && (
              <div style={{ padding: "12px", border: "1px solid #e0e0e0", borderRadius: "4px", marginBottom: "16px" }}>
                <div className="decision-flow">
                  {Object.entries(retrieval_metrics.decision_path).map(([key, value]) => (
                    <div key={key} style={{ display: "flex", alignItems: "center", marginBottom: "8px" }}>
                      <span
                        style={{
                          display: "inline-block",
                          width: "20px",
                          height: "20px",
                          borderRadius: "50%",
                          backgroundColor: value ? "#4CAF50" : "#ccc",
                          marginRight: "12px",
                        }}
                      />
                      <span style={{ fontWeight: value ? "bold" : "normal", color: value ? "#000" : "#666" }}>
                        {key.replace(/_/g, " ").toUpperCase()}: {value ? "✓ Yes" : "✗ No"}
                      </span>
                    </div>
                  ))}
                </div>

                {retrieval_metrics.search_parameters && (
                  <div style={{ marginTop: "16px", padding: "12px", backgroundColor: "#f9f9f9", borderRadius: "4px" }}>
                    <strong>Search Parameters:</strong>
                    <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                      <li>
                        <strong>Query:</strong> "{retrieval_metrics.search_parameters.query}"
                      </li>
                      <li>
                        <strong>Top K:</strong> {retrieval_metrics.search_parameters.top_k}
                      </li>
                      <li>
                        <strong>Embedder:</strong> {retrieval_metrics.search_parameters.embedder_type}
                      </li>
                      <li>
                        <strong>Web Search:</strong> {retrieval_metrics.search_parameters.enable_web_search ? "Enabled" : "Disabled"}
                      </li>
                      {retrieval_metrics.search_parameters.web_mode && (
                        <li>
                          <strong>Web Mode:</strong> {retrieval_metrics.search_parameters.web_mode}
                        </li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tier Breakdown */}
        {retrieval_metrics?.tier_breakdown && (
          <div className="metrics-section">
            <div
              className="metrics-section-header"
              onClick={() => toggleSection("tier-breakdown")}
              style={{ cursor: "pointer", padding: "12px", backgroundColor: "#f5f5f5", borderRadius: "4px", marginBottom: "8px" }}
            >
              <strong>📊 Tier Breakdown & Scores</strong>
              <span style={{ float: "right" }}>{expandedSection === "tier-breakdown" ? "▼" : "▶"}</span>
            </div>
            {expandedSection === "tier-breakdown" && (
              <div style={{ padding: "12px", border: "1px solid #e0e0e0", borderRadius: "4px", marginBottom: "16px" }}>
                {Object.entries(retrieval_metrics.tier_breakdown).map(([tier, data]) => {
                  if (data.count === 0) return null;
                  const tierNum = parseInt(tier.replace("tier_", ""));
                  return (
                    <div
                      key={tier}
                      style={{
                        marginBottom: "16px",
                        border: `2px solid ${getTierColor(tierNum)}`,
                        borderRadius: "8px",
                        padding: "12px",
                      }}
                    >
                      <div
                        onClick={() => toggleTier(tier)}
                        style={{ cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center" }}
                      >
                        <div>
                          <strong style={{ color: getTierColor(tierNum) }}>{getTierLabel(tierNum)}</strong>
                          <div style={{ marginTop: "4px", fontSize: "14px", color: "#666" }}>
                            <span>
                              {data.count} documents | Avg Score: {formatScore(data.avg_score)} | Max Score: {formatScore(data.max_score)}
                            </span>
                          </div>
                        </div>
                        <span>{expandedTier === tier ? "▼" : "▶"}</span>
                      </div>

                      {expandedTier === tier && (
                        <div style={{ marginTop: "12px" }}>
                          {data.documents.map((doc: any, idx: number) => (
                            <div
                              key={idx}
                              style={{
                                padding: "12px",
                                backgroundColor: "#f9f9f9",
                                borderRadius: "4px",
                                marginTop: "8px",
                                borderLeft: `4px solid ${getTierColor(tierNum)}`,
                              }}
                            >
                              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                                <strong>Rank #{doc.rank}</strong>
                                <span style={{ fontFamily: "monospace", backgroundColor: "#e0e0e0", padding: "2px 8px", borderRadius: "4px" }}>
                                  Score: {formatScore(doc.score)}
                                </span>
                              </div>
                              <div style={{ fontSize: "13px", color: "#666", marginBottom: "4px" }}>
                                <strong>Title:</strong> {doc.title}
                              </div>
                              <div style={{ fontSize: "13px", color: "#666", marginBottom: "4px" }}>
                                <strong>Path:</strong> {doc.source_path}
                              </div>
                              {doc.url && (
                                <div style={{ fontSize: "13px", color: "#666", marginBottom: "4px" }}>
                                  <strong>URL:</strong>{" "}
                                  <a href={doc.url} target="_blank" rel="noopener noreferrer">
                                    {doc.url}
                                  </a>
                                </div>
                              )}
                              {doc.trust_score !== undefined && (
                                <div style={{ fontSize: "13px", color: "#666", marginBottom: "4px" }}>
                                  <strong>Trust Score:</strong> {formatScore(doc.trust_score)}
                                </div>
                              )}
                              <div style={{ fontSize: "12px", color: "#888", marginTop: "8px", fontStyle: "italic" }}>
                                {doc.chunk_text}
                              </div>
                              <div style={{ marginTop: "8px", fontSize: "12px" }}>
                                {doc.rrf_score && (
                                  <span style={{ marginRight: "12px" }}>
                                    <strong>RRF Score:</strong> {formatScore(doc.rrf_score)}
                                  </span>
                                )}
                                {doc.similarity_score && (
                                  <span>
                                    <strong>Similarity Score:</strong> {formatScore(doc.similarity_score)}
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Generation Reasoning */}
        {generation_reasoning && (
          <div className="metrics-section">
            <div
              className="metrics-section-header"
              onClick={() => toggleSection("generation")}
              style={{ cursor: "pointer", padding: "12px", backgroundColor: "#f5f5f5", borderRadius: "4px", marginBottom: "8px" }}
            >
              <strong>🤖 LLM Generation Reasoning</strong>
              <span style={{ float: "right" }}>{expandedSection === "generation" ? "▼" : "▶"}</span>
            </div>
            {expandedSection === "generation" && (
              <div style={{ padding: "12px", border: "1px solid #e0e0e0", borderRadius: "4px", marginBottom: "16px" }}>
                <div style={{ marginBottom: "16px" }}>
                  <strong>Model Used:</strong> <code>{generation_reasoning.model_used}</code>
                </div>

                <div style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#f9f9f9", borderRadius: "4px" }}>
                  <strong>Context Selection:</strong>
                  <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                    <li>Total Retrieved: {generation_reasoning.context_selection.total_retrieved}</li>
                    <li>Used in Prompt: {generation_reasoning.context_selection.used_in_prompt}</li>
                    <li>Truncated Docs: {generation_reasoning.context_selection.truncated_docs}</li>
                  </ul>
                  <div style={{ marginTop: "8px", fontStyle: "italic", color: "#666" }}>{generation_reasoning.context_selection.reasoning}</div>
                </div>

                <div style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#f9f9f9", borderRadius: "4px" }}>
                  <strong>Document Ranking:</strong>
                  <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                    <li>
                      Sort Method: <code>{generation_reasoning.document_ranking.sort_method}</code>
                    </li>
                    <li>{generation_reasoning.document_ranking.description}</li>
                  </ul>
                </div>

                <div style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#f9f9f9", borderRadius: "4px" }}>
                  <strong>Prompt Structure:</strong>
                  <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                    <li>
                      Type: <code>{generation_reasoning.prompt_structure.type}</code>
                    </li>
                    <li>Instructions: {generation_reasoning.prompt_structure.instructions}</li>
                    <li>Temperature: {generation_reasoning.prompt_structure.temperature}</li>
                    <li>Max Response Tokens: {generation_reasoning.prompt_structure.max_response_tokens}</li>
                  </ul>
                </div>

                <div style={{ padding: "12px", backgroundColor: "#e8f5e9", borderRadius: "4px", borderLeft: "4px solid #4CAF50" }}>
                  <strong>Citations Found:</strong> {generation_reasoning.citations_found} references extracted from answer
                </div>
              </div>
            )}
          </div>
        )}

        {/* All Retrieved Documents */}
        {retrieval_metrics?.documents && retrieval_metrics.documents.length > 0 && (
          <div className="metrics-section">
            <div
              className="metrics-section-header"
              onClick={() => toggleSection("all-docs")}
              style={{ cursor: "pointer", padding: "12px", backgroundColor: "#f5f5f5", borderRadius: "4px", marginBottom: "8px" }}
            >
              <strong>📄 All Retrieved Documents ({retrieval_metrics.documents.length})</strong>
              <span style={{ float: "right" }}>{expandedSection === "all-docs" ? "▼" : "▶"}</span>
            </div>
            {expandedSection === "all-docs" && (
              <div style={{ padding: "12px", border: "1px solid #e0e0e0", borderRadius: "4px", marginBottom: "16px" }}>
                <div style={{ maxHeight: "400px", overflowY: "auto" }}>
                  {retrieval_metrics.documents.map((doc, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "12px",
                        backgroundColor: idx % 2 === 0 ? "#fff" : "#f9f9f9",
                        borderLeft: `4px solid ${getTierColor(doc.tier)}`,
                        marginBottom: "8px",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                        <div>
                          <strong>#{doc.rank}</strong> - {getTierLabel(doc.tier)}
                        </div>
                        <span style={{ fontFamily: "monospace", fontSize: "14px", backgroundColor: "#e0e0e0", padding: "4px 8px", borderRadius: "4px" }}>
                          {formatScore(doc.score)}
                        </span>
                      </div>
                      <div style={{ fontSize: "13px", color: "#333" }}>
                        <strong>{doc.title}</strong>
                      </div>
                      <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>{doc.source_path}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};

export default SearchMetrics;
