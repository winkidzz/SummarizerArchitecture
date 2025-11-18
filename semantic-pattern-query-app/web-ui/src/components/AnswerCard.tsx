import type { QueryResponse } from "../lib/api";

interface AnswerCardProps {
  result: QueryResponse;
}

const AnswerCard = ({ result }: AnswerCardProps) => {
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
    </section>
  );
};

export default AnswerCard;
