import type { SourceDocument } from "../lib/api";

interface SourcesListProps {
  sources: SourceDocument[];
}

const SourcesList = ({ sources }: SourcesListProps) => {
  if (!sources.length) {
    return null;
  }

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
        {sources.map((source, index) => (
          <li key={`${source.document_id ?? "source"}-${index}`}>
            <div className="source-title">
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
        ))}
      </ul>
    </section>
  );
};

export default SourcesList;
