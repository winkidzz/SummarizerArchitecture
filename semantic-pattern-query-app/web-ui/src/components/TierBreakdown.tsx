import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { SourceDocument } from "../lib/api";
import { fetchDocumentContent } from "../lib/api";

interface TierBreakdownProps {
  sources: SourceDocument[];
}

const TierBreakdown = ({ sources }: TierBreakdownProps) => {
  const [selectedDoc, setSelectedDoc] = useState<{
    path: string;
    id: string;
    content: string;
    extension: string;
    loading: boolean;
  } | null>(null);

  if (!sources.length) {
    return null;
  }

  const handleDocumentClick = async (source: SourceDocument) => {
    const path = source.source_path;
    if (!path) return;

    // Extract file extension from path
    const extension = path.split('.').pop()?.toLowerCase() || "";

    setSelectedDoc({
      path,
      id: source.document_id ?? "Unknown",
      content: "",
      extension,
      loading: true,
    });

    try {
      const result = await fetchDocumentContent(path);
      setSelectedDoc((prev) =>
        prev
          ? {
              ...prev,
              content: result.content,
              extension: result.metadata.extension?.replace('.', '').toLowerCase() || extension,
              loading: false
            }
          : null
      );
    } catch (error) {
      setSelectedDoc((prev) =>
        prev
          ? {
              ...prev,
              content: `Error loading document: ${
                error instanceof Error ? error.message : "Unknown error"
              }`,
              loading: false,
            }
          : null
      );
    }
  };

  const closeModal = () => {
    setSelectedDoc(null);
  };

  // Group sources by tier
  const tier1Sources = sources.filter((s) => {
    const metadata = s as Record<string, unknown>;
    const sourceType = metadata.source_type ?? metadata.layer;
    return !sourceType || (sourceType !== "web_search" && sourceType !== "web_knowledge_base");
  });

  const tier2Sources = sources.filter((s) => {
    const metadata = s as Record<string, unknown>;
    const sourceType = metadata.source_type ?? metadata.layer;
    return sourceType === "web_knowledge_base";
  });

  const tier3Sources = sources.filter((s) => {
    const metadata = s as Record<string, unknown>;
    const sourceType = metadata.source_type ?? metadata.layer;
    return sourceType === "web_search";
  });

  const renderTierSection = (
    tierNum: number,
    tierSources: SourceDocument[],
    title: string,
    description: string,
    color: string
  ) => {
    if (tierSources.length === 0) return null;

    return (
      <div className="tier-section" style={{ marginBottom: "20px" }}>
        <div
          style={{
            backgroundColor: color,
            color: "white",
            padding: "12px 16px",
            borderRadius: "8px 8px 0 0",
            fontWeight: "600",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <span style={{ fontSize: "0.9rem", opacity: 0.9 }}>Tier {tierNum}</span>
            <span style={{ marginLeft: "12px", fontSize: "1rem" }}>{title}</span>
          </div>
          <span
            style={{
              backgroundColor: "rgba(255,255,255,0.2)",
              padding: "4px 12px",
              borderRadius: "12px",
              fontSize: "0.9rem",
            }}
          >
            {tierSources.length} results
          </span>
        </div>
        <div
          style={{
            border: `2px solid ${color}`,
            borderTop: "none",
            borderRadius: "0 0 8px 8px",
            padding: "12px",
            backgroundColor: "rgba(0,0,0,0.02)",
          }}
        >
          <p style={{ margin: "0 0 12px 0", fontSize: "0.85rem", color: "#666" }}>
            {description}
          </p>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {tierSources.map((source, index) => (
              <li
                key={`${source.document_id ?? "source"}-${index}`}
                onClick={() => handleDocumentClick(source)}
                style={{
                  padding: "10px",
                  marginBottom: "8px",
                  backgroundColor: "white",
                  borderRadius: "6px",
                  border: "1px solid #e5e7eb",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "#f9fafb";
                  e.currentTarget.style.borderColor = color;
                  e.currentTarget.style.transform = "translateX(4px)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "white";
                  e.currentTarget.style.borderColor = "#e5e7eb";
                  e.currentTarget.style.transform = "translateX(0)";
                }}
              >
                <div style={{ fontWeight: "500", marginBottom: "4px", fontSize: "0.9rem", color: color }}>
                  📄 {source.document_id ?? `Document ${index + 1}`}
                </div>
                <div style={{ fontSize: "0.8rem", color: "#6b7280", marginBottom: "4px" }}>
                  {source.document_type ?? "pattern"}
                  {typeof source.score === "number" && (
                    <span style={{ marginLeft: "12px", fontWeight: "500" }}>
                      Score: {source.score.toFixed(3)}
                    </span>
                  )}
                </div>
                <div style={{ fontSize: "0.75rem", color: "#9ca3af" }}>
                  {source.source_path ?? "—"}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  return (
    <>
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">3-Tier Retrieval Breakdown</p>
            <h2>Results by tier</h2>
          </div>
          <span className="badge">{sources.length} total</span>
        </div>

        <div style={{ padding: "16px" }}>
          {renderTierSection(
            1,
            tier1Sources,
            "Pattern Library",
            "Results from local Qdrant vector store and Elasticsearch BM25 hybrid search",
            "#10b981"
          )}

          {renderTierSection(
            2,
            tier2Sources,
            "Web Knowledge Base (Cached)",
            "Previously ingested web search results stored in Qdrant",
            "#3b82f6"
          )}

          {renderTierSection(
            3,
            tier3Sources,
            "Live Web Search",
            "Fresh results from DuckDuckGo, extracted and auto-ingested into Web KB",
            "#8b5cf6"
          )}

          {tier1Sources.length === 0 && tier2Sources.length === 0 && tier3Sources.length === 0 && (
            <div
              style={{
                padding: "20px",
                textAlign: "center",
                color: "#6b7280",
                fontSize: "0.9rem",
              }}
            >
              No results found in any tier
            </div>
          )}
        </div>
      </section>

      {/* Document Content Modal */}
      {selectedDoc && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "20px",
          }}
          onClick={closeModal}
        >
          <div
            style={{
              backgroundColor: "white",
              borderRadius: "12px",
              maxWidth: "900px",
              width: "100%",
              maxHeight: "90vh",
              display: "flex",
              flexDirection: "column",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div
              style={{
                padding: "20px 24px",
                borderBottom: "1px solid #e5e7eb",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <h3 style={{ margin: 0, fontSize: "1.25rem", fontWeight: "600" }}>
                  {selectedDoc.id}
                </h3>
                <p style={{ margin: "4px 0 0 0", fontSize: "0.875rem", color: "#6b7280" }}>
                  {selectedDoc.path}
                </p>
              </div>
              <button
                onClick={closeModal}
                style={{
                  background: "none",
                  border: "none",
                  fontSize: "1.5rem",
                  cursor: "pointer",
                  color: "#6b7280",
                  padding: "4px 8px",
                }}
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div
              style={{
                padding: "24px",
                overflowY: "auto",
                flex: 1,
              }}
            >
              {selectedDoc.loading ? (
                <div style={{ textAlign: "center", padding: "40px", color: "#6b7280" }}>
                  Loading document content...
                </div>
              ) : selectedDoc.extension === "md" ? (
                <div
                  style={{
                    fontSize: "0.875rem",
                    lineHeight: "1.6",
                    color: "#1f2937",
                  }}
                  className="markdown-content"
                >
                  <ReactMarkdown>{selectedDoc.content}</ReactMarkdown>
                </div>
              ) : (
                <pre
                  style={{
                    whiteSpace: "pre-wrap",
                    wordWrap: "break-word",
                    fontFamily: "ui-monospace, monospace",
                    fontSize: "0.875rem",
                    lineHeight: "1.6",
                    margin: 0,
                  }}
                >
                  {selectedDoc.content}
                </pre>
              )}
            </div>

            {/* Modal Footer */}
            <div
              style={{
                padding: "16px 24px",
                borderTop: "1px solid #e5e7eb",
                display: "flex",
                justifyContent: "flex-end",
              }}
            >
              <button
                onClick={closeModal}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#3b82f6",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "0.875rem",
                  fontWeight: "500",
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TierBreakdown;
