import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { SourceDocument } from "../lib/api";
import { fetchDocumentContent } from "../lib/api";

interface SourcesListProps {
  sources: SourceDocument[];
}

const SourcesList = ({ sources }: SourcesListProps) => {
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

  const getTierBadge = (source: SourceDocument): string => {
    const metadata = source as Record<string, unknown>;
    const sourceType = metadata.source_type ?? metadata.layer;

    if (sourceType === "web_search") return "T3";
    if (sourceType === "web_knowledge_base") return "T2";
    return "T1";
  };

  const getTierColor = (tier: string): string => {
    if (tier === "T3") return "#8b5cf6"; // Purple for live web
    if (tier === "T2") return "#3b82f6"; // Blue for web cache
    return "#10b981"; // Green for pattern library
  };

  return (
    <>
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Sources</p>
            <h2>Supporting documents</h2>
          </div>
          <span className="badge">{sources.length}</span>
        </div>

        <ul className="source-list">
        {sources.map((source, index) => {
          const tier = getTierBadge(source);
          const tierColor = getTierColor(tier);

          return (
            <li
              key={`${source.document_id ?? "source"}-${index}`}
              onClick={() => handleDocumentClick(source)}
              style={{ cursor: "pointer" }}
            >
              <div className="source-title">
                <span
                  style={{
                    display: "inline-block",
                    backgroundColor: tierColor,
                    color: "white",
                    fontSize: "0.7rem",
                    fontWeight: "bold",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    marginRight: "8px",
                  }}
                >
                  {tier}
                </span>
                📄 {source.document_id ?? `Source ${index + 1}`}
              </div>
              <div className="source-meta">
                <span>{source.document_type ?? "pattern"}</span>
                {typeof source.score === "number" && (
                  <span className="score">Score: {source.score.toFixed(3)}</span>
                )}
              </div>
              <p className="source-path">{source.source_path ?? "—"}</p>
            </li>
          );
        })}
        </ul>
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

export default SourcesList;
