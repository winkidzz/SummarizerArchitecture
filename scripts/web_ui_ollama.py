#!/usr/bin/env python3
"""
Simple web UI for querying patterns using Ollama (Gemma3:4b).
100% local - no API keys required.
"""

import sys
from pathlib import Path

# Add paths
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os

# Direct imports to avoid relative import issues
from document_store.orchestrator import DocumentStoreOrchestrator

app = FastAPI(title="Pattern Query - Ollama")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
orchestrator = None

@app.on_event("startup")
async def startup():
    global orchestrator
    orchestrator = DocumentStoreOrchestrator(
        persist_directory="data/chroma_db",
        collection_name="architecture_patterns",
        use_adk_agent=False,
        ollama_model=OLLAMA_MODEL,
    )

class QueryRequest(BaseModel):
    query: str
    n_results: int = 5

@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pattern Query - {OLLAMA_MODEL}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            input[type="text"] {{
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 16px;
                margin-bottom: 15px;
            }}
            button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 30px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
            }}
            button:disabled {{
                opacity: 0.6;
            }}
            #result {{
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 6px;
            }}
            .loading {{
                text-align: center;
                padding: 40px;
            }}
            .spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .examples {{
                background: #e8f4f8;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
            }}
            .example-query {{
                display: inline-block;
                background: white;
                padding: 8px 15px;
                margin: 5px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
            }}
            .example-query:hover {{
                background: #667eea;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Pattern Query Agent</h1>
            <p>💻 Model: <strong>{OLLAMA_MODEL}</strong></p>
            <p>🔒 100% Local - No API Keys</p>
        </div>

        <div class="container">
            <div class="examples">
                <h3>💡 Try these questions:</h3>
                <span class="example-query" onclick="setQuery('What RAG patterns are available?')">RAG patterns</span>
                <span class="example-query" onclick="setQuery('Explain Contextual Retrieval')">Contextual Retrieval</span>
                <span class="example-query" onclick="setQuery('How do I implement RAG with Vertex AI?')">Vertex AI</span>
                <span class="example-query" onclick="setQuery('Compare RAPTOR vs basic RAG')">RAPTOR comparison</span>
            </div>

            <input type="text" id="query" placeholder="Ask about patterns..." autofocus>
            <button onclick="ask()" id="btn">Ask Question</button>

            <div id="result"></div>
        </div>

        <script>
            function setQuery(q) {{
                document.getElementById('query').value = q;
            }}

            async function ask() {{
                const query = document.getElementById('query').value;
                const btn = document.getElementById('btn');
                const result = document.getElementById('result');

                if (!query) return;

                btn.disabled = true;
                result.innerHTML = '<div class="loading"><div class="spinner"></div><p>Thinking...</p></div>';

                try {{
                    const res = await fetch('/query', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{query, n_results: 5}})
                    }});

                    const data = await res.json();

                    let html = '<h3>🤖 Response:</h3>';
                    html += '<p style="white-space: pre-wrap;">' + (data.response || 'No response') + '</p>';
                    html += '<p><small>Retrieved ' + (data.num_results || 0) + ' documents</small></p>';

                    result.innerHTML = html;
                }} catch (e) {{
                    result.innerHTML = '<p style="color:red;">Error: ' + e.message + '</p>';
                }} finally {{
                    btn.disabled = false;
                }}
            }}

            document.getElementById('query').addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') ask();
            }});
        </script>
    </body>
    </html>
    """

@app.post("/query")
async def query(req: QueryRequest):
    try:
        result = orchestrator.query_patterns(
            query=req.query,
            n_results=req.n_results,
            use_agent=False,
            use_ollama_rag=True,
        )

        return {
            "response": result.get("response", "No response"),
            "num_results": len(result.get("results", [])),
            "model": OLLAMA_MODEL
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"\n{'='*70}")
    print(f"🤖 Pattern Query Web UI")
    print(f"{'='*70}\n")
    print(f"💻 Model: {OLLAMA_MODEL}")
    print(f"📍 URL: http://127.0.0.1:{port}\n")
    print(f"Press Ctrl+C to stop\n")

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
