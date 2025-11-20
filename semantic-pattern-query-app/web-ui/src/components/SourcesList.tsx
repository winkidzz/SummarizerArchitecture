import type { SourceDocument } from "../lib/api";

interface SourcesListProps {
  sources: SourceDocument[];
}

const SourcesList = ({ sources }: SourcesListProps) => {
  if (!sources.length) {
    return null;
  }

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
            <li key={`${source.document_id ?? "source"}-${index}`}>
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
                {source.document_id ?? `Source ${index + 1}`}
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
  );
};

export default SourcesList;
