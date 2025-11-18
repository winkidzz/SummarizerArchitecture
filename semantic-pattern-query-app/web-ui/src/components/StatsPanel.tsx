import type { SystemStats } from "../lib/api";

interface StatsPanelProps {
  stats: SystemStats | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

const StatsPanel = ({ stats, loading, error, onRefresh }: StatsPanelProps) => {
  const embeddingSummary = stats?.embedding_models
    ? Object.entries(stats.embedding_models)
        .map(([key, value]) => `${key}: ${value}`)
        .join(" · ")
    : undefined;

  type QdrantStats = {
    vector_size?: number;
    points_count?: number;
    [key: string]: unknown;
  };

  const qdrantStats: QdrantStats = (stats?.qdrant ?? {}) as QdrantStats;

  return (
    <section className="panel compact-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">System status</p>
          <h2>Retriever telemetry</h2>
        </div>
        <button
          className="ghost"
          type="button"
          disabled={loading}
          onClick={onRefresh}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {stats ? (
        <div className="stats-grid">
          <div>
            <p className="meta-label">Vector dimension</p>
            <p className="meta-value">
              {stats.vector_dimension ?? qdrantStats.vector_size ?? "—"}
            </p>
          </div>
          <div>
            <p className="meta-label">Embedding models</p>
            <p className="meta-value">
              {embeddingSummary ?? "Not reported by API"}
            </p>
          </div>
          <div>
            <p className="meta-label">Qdrant points</p>
            <p className="meta-value">
              {qdrantStats.points_count ?? "Unknown"}
            </p>
          </div>
        </div>
      ) : (
        <p className="muted">
          Stats will appear after the FastAPI server responds.
        </p>
      )}
    </section>
  );
};

export default StatsPanel;
