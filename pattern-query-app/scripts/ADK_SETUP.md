# Google ADK Setup Checklist

This guide shows how to bootstrap the Google Agent Development Kit (ADK) so it
can query the local ChromaDB knowledge base that powers the AI Summarization
Reference Architecture.

> **TL;DR**
>
> ```bash
> pip install google-adk==1.18.0
> export GOOGLE_API_KEY="..."        # from https://aistudio.google.com/app/apikey
> python scripts/setup_adk_agent.py
> scripts/start_adk_default_ui.sh    # or: adk run .adk/agents/gemini_agent
> ```

## 1. Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.9+ | 3.11+ recommended for best ADK performance |
| `pip` / `uv` | Install dependencies (`pip install -r requirements.txt`) |
| Google ADK 1.18.0 | Added to `requirements.txt`; install manually with `pip install google-adk==1.18.0` if needed |
| Google AI API key | Required for Gemini (`https://aistudio.google.com/app/apikey`) |

Optional (only if you want to use the standalone `adk-web` repository instead
of the built-in UI):

| Requirement | Notes |
|-------------|-------|
| Node.js 18+ | Needed to build/run the Angular-based ADK Web dev UI |
| Angular CLI | `npm install -g @angular/cli` |

## 2. Generate the Agent Package

The repository ships with a ready-to-use agent under `.adk/agents/gemini_agent`.
Regenerate or customize it at any time using:

```bash
python scripts/setup_adk_agent.py \
  --persist-directory data/chroma_db \
  --collection-name architecture_patterns \
  --model gemini-2.5-flash \
  --agent-name chromadb_pattern_agent
```

Key flags:

| Flag | Description |
|------|-------------|
| `--persist-directory` | Relative or absolute path to the ChromaDB persistence folder |
| `--collection-name` | Target collection name (defaults to `architecture_patterns`) |
| `--model` | Default Gemini model (`gemini-2.5-flash`, `gemini-1.5-pro`, etc.) |
| `--agent-name` | Friendly identifier shown inside ADK |
| `--instruction-file` | Optional Markdown/text file with a custom system prompt |
| `--overwrite` | Force regeneration even if `.adk/agents/gemini_agent/agent.py` already exists |

The script:
1. Creates `.adk/agents/gemini_agent`.
2. Writes `agent.py` that wires the ADK agent to `DocumentStoreOrchestrator`.
3. Ensures the package’s `__init__.py` is present so the ADK CLI can auto-load it.

## 3. Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_API_KEY` | Required for Gemini access |
| `ADK_MODEL` | Override the default Gemini model per shell/session |
| `ADK_PERSIST_DIRECTORY` | Point ADK at a different ChromaDB folder |
| `ADK_COLLECTION_NAME` | Use a different vector-store collection |
| `ADK_INSTRUCTION` | Inject a custom system prompt (instead of editing `agent.py`) |
| `ADK_WEB_HOST` / `ADK_WEB_PORT` | Configure `scripts/start_adk_default_ui.sh` |
| `ADK_ALLOW_ORIGINS` | Additional CORS origins for the web UI |

Save these in `.env` (gitignored) or export them before running the CLI.

## 4. Running the Agent

### 4.1 Interactive CLI

```bash
adk run .adk/agents/gemini_agent
```

This opens the built-in REPL. Ask natural-language questions; the agent will call
the bundled `query_architecture_patterns` tool to retrieve context from ChromaDB.

### 4.2 Default Web UI

```bash
scripts/start_adk_default_ui.sh
```

This script simply wraps `adk web --host … --port … .adk/agents`, so you get the
FastAPI + default UI experience without remembering the flags. Use `Ctrl+C` to stop.

### 4.3 Custom UI (Optional)

If you want to hack on the Angular UI:

```bash
git clone https://github.com/google/adk-web.git
cd adk-web
npm install
npm run serve -- --backend=http://localhost:8000
```

In another terminal, run:

```bash
adk api_server --host=0.0.0.0 --port=8000 --allow_origins=http://localhost:4200 .adk/agents
```

## 5. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: google.adk` | Run `pip install google-adk==1.18.0` (or `pip install -r requirements.txt`) |
| `GOOGLE_API_KEY not set` | Export the key or add it to `.env` before launching ADK |
| `adk: command not found` | Ensure your Python scripts directory is on `PATH` |
| ChromaDB empty | Run the document store ingestion workflow (`python scripts/initialize_and_test.py`) to populate data before querying |
| Web UI CORS errors | Set `ADK_ALLOW_ORIGINS="*"` (or the correct origin) before launching the UI script |

## 6. Related Files

| File | Purpose |
|------|---------|
| `.adk/agents/gemini_agent/agent.py` | Source for the ADK agent that connects to `DocumentStoreOrchestrator` |
| `scripts/setup_adk_agent.py` | Generates/updates the agent package |
| `scripts/start_adk_default_ui.sh` | Convenience wrapper around `adk web` |
| `docs/agent-setup-guide.md` | High-level narrative for ADK + Ollama usage |

Happy agent building!
