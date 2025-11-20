import type { QueryResponse } from "../lib/api";

interface AnswerCardProps {
  result: QueryResponse;
}

const AnswerCard = ({ result }: AnswerCardProps) => {
  const stats = result.retrieval_stats;
  const tier1 = stats?.tier_1_results ?? 0;
  const tier2 = stats?.tier_2_results ?? 0;
  const tier3 = stats?.tier_3_results ?? 0;
  const hasTierData = stats && (tier1 > 0 || tier2 > 0 || tier3 > 0);

  return (
    <section className="panel answer-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Response</p>
          <h2>Architecture guidance</h2>
        </div>
        <span className={`status-pill ${result.cache_hit ? "success" : ""}`}>
          {result.cache_hit ? "Cache hit" : "Fresh retrieval"}
        </span>
      </div>

      <p className="answer-text">{result.answer}</p>

      <div className="metadata-grid">
        <div>
          <p className="meta-label">Documents retrieved</p>
          <p className="meta-value">{result.retrieved_docs ?? "—"}</p>
        </div>
        <div>
          <p className="meta-label">Context docs used</p>
          <p className="meta-value">
            {result.context_docs_used ?? result.sources.length}
          </p>
        </div>
        <div>
          <p className="meta-label">Citations returned</p>
          <p className="meta-value">{result.sources.length}</p>
        </div>
      </div>

      {hasTierData && (
        <div className="tier-breakdown">
          <p className="meta-label" style={{ marginBottom: "8px" }}>
            3-Tier Retrieval Breakdown
          </p>
          <div className="metadata-grid">
            <div>
              <p className="meta-label">Tier 1 (Pattern Library)</p>
              <p className="meta-value">{tier1}</p>
            </div>
            <div>
              <p className="meta-label">Tier 2 (Web KB Cache)</p>
              <p className="meta-value">{tier2}</p>
            </div>
            <div>
              <p className="meta-label">Tier 3 (Live Web)</p>
              <p className="meta-value">{tier3}</p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default AnswerCard;
