# Google ADK Implementation Guide

Google's Agent Development Kit (ADK) is the primary agent framework for this
project. It provides a first-class tool ecosystem, observability hooks, and an
out-of-the-box web UI for testing the architecture knowledge base.

## Overview

| Capability | Details |
|------------|---------|
| **Models** | Gemini family (2.5 Flash, 1.5 Pro, Ultra) + on-prem adapters |
| **Tooling** | Function tools, built-in Google Search, MCP integrations, plugin system |
| **Observability** | Token usage, event timelines, tracing hooks, logging plugins |
| **Security** | Model Armor, tool confirmation, credential services, context filtering |
| **UI** | `adk web` default UI, optional Angular `adk-web` project |
| **Deployments** | Local dev server, Cloud Run, Agent Engine |

## Prerequisites

- Python 3.9+ (3.11+ recommended).
- `google-adk>=1.18.0` (included in `requirements.txt`).
- Google AI API key (`GOOGLE_API_KEY` environment variable).
- Populated ChromaDB store (run `python scripts/initialize_and_test.py` first).

Optional:

- Node.js + Angular CLI (only if you need to run the `adk-web` repository).
- Google Cloud project/credentials for Agent Engine deployments.

## Setup Steps

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate/update the agent**
   ```bash
   python scripts/setup_adk_agent.py \
     --persist-directory data/chroma_db \
     --collection-name architecture_patterns \
     --model gemini-2.5-flash
   ```

   This script writes `.adk/agents/chromadb_agent/agent.py`, which wires ADK to
   `DocumentStoreOrchestrator`. Pass `--instruction-file` to inject a custom
   system prompt or `--overwrite` to rebuild the file.

3. **Launch a UI**
   ```bash
   scripts/start_adk_default_ui.sh      # wraps `adk web`
   # or: adk run .adk/agents/chromadb_agent
   ```

4. **Customize via environment variables**

   | Variable | Purpose |
   |----------|---------|
   | `GOOGLE_API_KEY` | Gemini access |
   | `ADK_MODEL` | Override the default model per shell |
   | `ADK_PERSIST_DIRECTORY` / `ADK_COLLECTION_NAME` | Point ADK at another ChromaDB location |
   | `ADK_INSTRUCTION` | Provide a custom system prompt |
   | `ADK_WEB_HOST`, `ADK_WEB_PORT`, `ADK_ALLOW_ORIGINS` | Configure `scripts/start_adk_default_ui.sh` |

5. **Troubleshoot / iterate** using `scripts/ADK_SETUP.md`, which contains the
   full checklist and remediation tips.

## Tooling Integration

The agent exposes two local tools implemented with `google.adk.tools.FunctionTool`:

| Tool | Description |
|------|-------------|
| `query_architecture_patterns` | Calls `DocumentStoreOrchestrator.query_patterns`, returning vector hits (content, metadata, ids). |
| `get_store_info` | Returns Chroma collection stats for quick health checks. |

Agents are instructed to call `query_architecture_patterns` for every question,
ensuring answers cite canonical IDs/metadata from the knowledge base.

## Programmatic Access

For inline use (e.g., within `DocumentStoreOrchestrator`), the
`ADKAgentQuery` class instantiates an ADK agent + `InMemoryRunner` when
`google-adk` is available. The runner:

1. Creates a transient session for each query.
2. Sends the user's question as `google.genai.types.Content`.
3. Streams ADK `Event` objects until a final response is produced.
4. Returns both the structured vector results and the ADK-composed answer.

If ADK is not installed (or fails to initialize), the code gracefully falls
back to the direct RAG interface.

## Observability & Security

- **Logging/Tracing**: Use `google.adk.plugins.LoggingPlugin` or custom plugins
  for detailed event logs. Tracing hooks integrate with OpenTelemetry
  exporters bundled in the dependency.
- **Model Armor**: Enable prompt-injection scanning via ADK's Model Armor
  features when deploying to production.
- **Tool confirmation**: Wrap critical tools with `require_confirmation=True`
  to introduce human-in-the-loop approvals (not needed for read-only queries).
- **Credential services**: When deploying beyond local dev, wire `Runner` to a
  credential service instead of relying solely on `GOOGLE_API_KEY`.

## Deployment Notes

| Target | Notes |
|--------|-------|
| Local dev | `InMemoryRunner` + `adk run`/`adk web` (current repo defaults). |
| Cloud Run | Package `.adk/agents/chromadb_agent` and run `adk deploy cloud_run ...`. Set env vars for Chroma paths. |
| Agent Engine | `adk deploy agent_engine --project <proj> --region <region>`. Useful when combining with other Google Cloud services. |

Ensure the ChromaDB directory is accessible (Cloud Run/Agent Engine may need it
mounted or replicated via Vertex AI Search, AlloyDB, etc., if you prefer a
managed vector store).

## References

- `scripts/ADK_SETUP.md` – detailed checklist.
- `docs/agent-setup-guide.md` – narrative covering ADK + Ollama.
- [Official ADK docs](https://google.github.io/adk-docs) – latest CLI/API reference.
