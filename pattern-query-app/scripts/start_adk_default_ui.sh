#!/usr/bin/env bash
# Launch the Google ADK default web UI against the local chromadb_agent.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="${ROOT_DIR}/.adk/agents"
HOST="${ADK_WEB_HOST:-127.0.0.1}"
PORT="${ADK_WEB_PORT:-8000}"
ALLOW_ORIGINS="${ADK_ALLOW_ORIGINS:-http://localhost:4200}"

if ! command -v adk >/dev/null 2>&1; then
  echo "Error: the 'adk' CLI is not on PATH. Install google-adk first." >&2
  exit 1
fi

if [ ! -d "${AGENTS_DIR}" ]; then
  echo "Error: ${AGENTS_DIR} does not exist. Run scripts/setup_adk_agent.py first." >&2
  exit 1
fi

echo "Starting ADK web UI on ${HOST}:${PORT} (agents: ${AGENTS_DIR})"
echo "Press Ctrl+C to stop."

cd "${ROOT_DIR}"
adk web --host="${HOST}" --port="${PORT}" --allow_origins="${ALLOW_ORIGINS}" "${AGENTS_DIR}"
