# Semantic Pattern Query UI

React + Vite single page app for querying the Healthcare AI Pattern Library through the FastAPI backend (`semantic-pattern-query-app/src/api_server.py`).

## Features

- Query form with support for cache toggling, Top-K configuration, and embedder selection (Ollama/Gemini)
- Displays synthesized answer, metadata, and supporting citations from the `/query` endpoint
- Shows live vector store stats pulled from `/stats`
- Configurable API base URL via Vite environment variables

## Getting Started

1. Ensure the FastAPI service is running (typically `uvicorn src.api_server:app --reload` in `semantic-pattern-query-app`).
2. Copy the environment template and adjust the API URL if necessary:
   ```bash
   cd semantic-pattern-query-app/web-ui
   cp .env.example .env    # Edit VITE_API_BASE_URL if backend is remote
   ```
3. Install dependencies and start the dev server:
   ```bash
   npm install
   npm run dev
   ```
4. Open the URL printed in the console (default `http://localhost:5173`).

## Available Scripts

- `npm run dev` – start Vite dev server with hot reload
- `npm run build` – type check and produce a production bundle in `dist/`
- `npm run preview` – serve the production bundle locally
- `npm run lint` – run the default ESLint checks

## Environment Variables

| Variable            | Description                              | Default                  |
| ------------------- | ---------------------------------------- | ------------------------ |
| `VITE_API_BASE_URL` | Base URL for the FastAPI server endpoints | `http://localhost:8000` |

Changes to `.env` require restarting `npm run dev`.
