import { type FormEvent, useState } from "react";
import type { QueryPayload } from "../lib/api";

interface QueryFormProps {
  loading: boolean;
  onSubmit: (payload: QueryPayload) => void;
}

type EmbedderOption = "auto" | "ollama" | "gemini";

const QueryForm = ({ loading, onSubmit }: QueryFormProps) => {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [useCache, setUseCache] = useState(true);
  const [embedder, setEmbedder] = useState<EmbedderOption>("auto");
  const [userNotes, setUserNotes] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) {
      return;
    }

    const payload: QueryPayload = {
      query: query.trim(),
      top_k: topK,
      use_cache: useCache,
    };

    if (embedder !== "auto") {
      payload.query_embedder_type = embedder;
    }

    if (userNotes.trim()) {
      payload.user_context = { notes: userNotes.trim() };
    }

    onSubmit(payload);
  };

  return (
    <form className="panel query-form" onSubmit={handleSubmit}>
      <div className="panel-header">
        <div>
          <p className="eyebrow">Architecture Assistant</p>
          <h2>Ask about a healthcare AI pattern</h2>
        </div>
        <button
          className="primary"
          disabled={loading || !query.trim()}
          type="submit"
        >
          {loading ? "Querying..." : "Run query"}
        </button>
      </div>

      <label className="input-label" htmlFor="query-input">
        Question
      </label>
      <textarea
        id="query-input"
        className="text-input"
        placeholder="e.g., How does contextual retrieval reduce hallucinations?"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        rows={4}
        disabled={loading}
      />

      <div className="field-grid">
        <label className="input-label" htmlFor="topk-input">
          Top K results
          <input
            id="topk-input"
            type="number"
            min={1}
            max={25}
            value={topK}
            onChange={(event) => setTopK(Number(event.target.value))}
            disabled={loading}
          />
        </label>

        <label className="input-label" htmlFor="embedder-input">
          Embedder
          <select
            id="embedder-input"
            value={embedder}
            onChange={(event) => setEmbedder(event.target.value as EmbedderOption)}
            disabled={loading}
          >
            <option value="auto">Auto (server default)</option>
            <option value="ollama">Ollama</option>
            <option value="gemini">Gemini</option>
          </select>
        </label>

        <label className="input-label checkbox-field">
          <input
            type="checkbox"
            checked={useCache}
            onChange={(event) => setUseCache(event.target.checked)}
            disabled={loading}
          />
          Use cache for repeated questions
        </label>
      </div>

      <label className="input-label" htmlFor="context-input">
        Optional context (stored as `notes` in `user_context`)
      </label>
      <textarea
        id="context-input"
        className="text-input"
        placeholder="Add hints such as care setting, preferred vendor, or compliance constraints."
        value={userNotes}
        onChange={(event) => setUserNotes(event.target.value)}
        rows={3}
        disabled={loading}
      />
    </form>
  );
};

export default QueryForm;
