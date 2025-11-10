#!/usr/bin/env python3
"""
Simple web interface for querying patterns using local Ollama models.

This provides a FastAPI-based web interface similar to ADK, but using
Ollama models instead of requiring a Google API key.
"""

import sys
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import os

# Import directly to avoid docling dependency
import importlib.util

# Load ollama_agent module
spec = importlib.util.spec_from_file_location(
    "ollama_agent",
    SRC_DIR / "document_store" / "agents" / "ollama_agent.py"
)
ollama_agent_module = importlib.util.module_from_spec(spec)
sys.modules["ollama_agent"] = ollama_agent_module
spec.loader.exec_module(ollama_agent_module)
OllamaAgent = ollama_agent_module.OllamaAgent

# Load vector_store module
spec = importlib.util.spec_from_file_location(
    "vector_store",
    SRC_DIR / "document_store" / "storage" / "vector_store.py"
)
vector_store_module = importlib.util.module_from_spec(spec)
sys.modules["vector_store"] = vector_store_module
spec.loader.exec_module(vector_store_module)
VectorStore = vector_store_module.VectorStore

app = FastAPI(title="Pattern Query - Ollama Agent")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:14b")
vector_store = VectorStore(
    persist_directory="data/chroma_db",
    collection_name="architecture_patterns"
)
agent = OllamaAgent(model=OLLAMA_MODEL, vector_store=vector_store)


class QueryRequest(BaseModel):
    query: str
    n_results: int = 5
    pattern_type: str = None
    vendor: str = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple web interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pattern Query - Ollama Agent</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .header h1 {
                margin: 0 0 10px 0;
            }
            .header p {
                margin: 5px 0;
                opacity: 0.9;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .input-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            input[type="text"], select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 30px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            #result {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .examples {
                background: #e8f4f8;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
            }
            .examples h3 {
                margin-top: 0;
                color: #0066cc;
            }
            .example-query {
                display: inline-block;
                background: white;
                padding: 8px 15px;
                margin: 5px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }
            .example-query:hover {
                background: #667eea;
                color: white;
            }
            pre {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 6px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Pattern Query Agent</h1>
            <p>💻 Model: <strong>""" + OLLAMA_MODEL + """</strong></p>
            <p>📚 Local ChromaDB with Architecture Patterns</p>
            <p>🔒 100% Local - No API Keys Required</p>
        </div>

        <div class="container">
            <div class="examples">
                <h3>💡 Example Queries (click to use):</h3>
                <span class="example-query" onclick="setQuery('What RAG patterns are available for healthcare?')">Healthcare RAG patterns</span>
                <span class="example-query" onclick="setQuery('Explain Contextual Retrieval')">Contextual Retrieval</span>
                <span class="example-query" onclick="setQuery('Compare RAPTOR RAG vs basic RAG')">RAPTOR vs Basic RAG</span>
                <span class="example-query" onclick="setQuery('How do I implement RAG with Google Vertex AI?')">Vertex AI RAG</span>
                <span class="example-query" onclick="setQuery('What is the best pattern for clinical notes?')">Clinical notes pattern</span>
            </div>

            <div class="input-group">
                <label for="query">🔍 Your Question:</label>
                <input type="text" id="query" placeholder="Ask about architecture patterns, RAG implementations, healthcare use cases...">
            </div>

            <div class="input-group">
                <label for="n_results">📊 Number of results:</label>
                <select id="n_results">
                    <option value="3">3 results</option>
                    <option value="5" selected>5 results</option>
                    <option value="10">10 results</option>
                </select>
            </div>

            <button onclick="queryPatterns()" id="queryBtn">Ask Question</button>

            <div id="result"></div>
        </div>

        <script>
            function setQuery(text) {
                document.getElementById('query').value = text;
                document.getElementById('query').focus();
            }

            async function queryPatterns() {
                const query = document.getElementById('query').value;
                const n_results = document.getElementById('n_results').value;
                const resultDiv = document.getElementById('result');
                const btn = document.getElementById('queryBtn');

                if (!query) {
                    alert('Please enter a question');
                    return;
                }

                btn.disabled = true;
                resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Querying patterns and generating response...</p></div>';

                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            query: query,
                            n_results: parseInt(n_results)
                        })
                    });

                    const data = await response.json();

                    if (data.error) {
                        resultDiv.innerHTML = `<h3 style="color: red;">Error</h3><p>${data.error}</p>`;
                    } else {
                        let html = '<h3>🤖 Response:</h3>';
                        html += `<p style="white-space: pre-wrap;">${data.response}</p>`;
                        html += '<h4>📚 Retrieved Documents:</h4>';
                        html += `<p>${data.num_results} relevant documents found</p>`;
                        if (data.results && data.results.length > 0) {
                            html += '<details><summary>View retrieved context</summary>';
                            html += '<pre>' + JSON.stringify(data.results, null, 2) + '</pre>';
                            html += '</details>';
                        }
                        resultDiv.innerHTML = html;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3 style="color: red;">Error</h3><p>${error.message}</p>`;
                } finally {
                    btn.disabled = false;
                }
            }

            // Allow Enter key to submit
            document.getElementById('query').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    queryPatterns();
                }
            });
        </script>
    </body>
    </html>
    """


@app.post("/query")
async def query_patterns(request: QueryRequest):
    """Query patterns using Ollama agent."""
    try:
        result = agent.query_with_rag(
            query=request.query,
            n_results=request.n_results,
            pattern_type=request.pattern_type,
            vendor=request.vendor,
        )

        return {
            "response": result.get("response", "No response generated"),
            "results": result.get("results", []),
            "num_results": len(result.get("results", [])),
            "model": OLLAMA_MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model": OLLAMA_MODEL,
        "agent": "OllamaAgent"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"\n{'='*70}")
    print(f"🤖 Pattern Query Agent - Local Ollama")
    print(f"{'='*70}")
    print(f"\n📍 Web Interface: http://127.0.0.1:{port}")
    print(f"💻 Model: {OLLAMA_MODEL}")
    print(f"📚 Data: ChromaDB (data/chroma_db)")
    print(f"\n🚀 Starting server...\n")

    uvicorn.run(app, host="127.0.0.1", port=port)
