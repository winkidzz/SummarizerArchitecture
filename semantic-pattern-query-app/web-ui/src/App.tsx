import { useEffect, useState } from "react";
import "./App.css";
import QueryForm from "./components/QueryForm";
import AnswerCard from "./components/AnswerCard";
import SourcesList from "./components/SourcesList";
import StatsPanel from "./components/StatsPanel";
import type { QueryPayload, QueryResponse, SystemStats } from "./lib/api";
import { API_BASE_URL, fetchStats, sendQuery } from "./lib/api";

function App() {
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const [stats, setStats] = useState<SystemStats | null>(null);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  const runQuery = async (payload: QueryPayload) => {
    setLoading(true);
    setError(null);
    setStatus("Running retrieval pipeline...");

    try {
      const response = await sendQuery(payload);
      setResult(response);
      setStatus(
        `Returned ${response.sources.length} citation${
          response.sources.length === 1 ? "" : "s"
        } across ${response.retrieved_docs ?? "?"} documents`
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to reach the API server."
      );
      setResult(null);
      setStatus(null);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    setStatsLoading(true);
    setStatsError(null);
    try {
      const data = await fetchStats();
      setStats(data);
    } catch (err) {
      setStatsError(
        err instanceof Error ? err.message : "Unable to load stats."
      );
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">Semantic Pattern Query App</p>
        <h1>Healthcare AI architecture search console</h1>
        <p className="muted">
          Connected to FastAPI at <code>{API_BASE_URL}</code>. The UI calls the
          `/query` endpoint to run the production RAG workflow.
        </p>
      </header>

      <main className="content-grid">
        <section className="primary-column">
          <QueryForm loading={loading} onSubmit={runQuery} />

          {status && !error && <p className="status-text">{status}</p>}

          {error && (
            <div className="panel error-panel" role="alert">
              <p className="eyebrow">Unable to complete query</p>
              <p>{error}</p>
            </div>
          )}

          {result ? (
            <>
              <AnswerCard result={result} />
              <SourcesList sources={result.sources} />
            </>
          ) : (
            <section className="panel placeholder-panel">
              <h2>Run your first query</h2>
              <p>
                Ask about RAPTOR RAG, contextual retrieval, compliance controls,
                or any other pattern documented in the library. The UI will show
                the generated answer, metadata, and supporting sources.
              </p>
              <ul>
                <li>“How does contextual retrieval reduce hallucinations?”</li>
                <li>“Compare RAPTOR RAG and multi-vector retrievers.”</li>
                <li>
                  “Which vendor blueprint covers prior-authorization document
                  intake?”
                </li>
              </ul>
            </section>
          )}
        </section>

        <section className="secondary-column">
          <StatsPanel
            stats={stats}
            loading={statsLoading}
            error={statsError}
            onRefresh={loadStats}
          />

          <section className="panel tips-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Tips</p>
                <h2>Better answers</h2>
              </div>
            </div>
            <ul>
              <li>
                Use the optional context box to describe care setting,
                regulatory constraints, or personas.
              </li>
              <li>
                Switch between Ollama and Gemini embedders to test cross-space
                performance.
              </li>
              <li>Disable caching to force a full retrieval and rerank cycle.</li>
            </ul>
          </section>
        </section>
      </main>
    </div>
  );
}

export default App;
