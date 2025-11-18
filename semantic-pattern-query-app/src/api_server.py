"""
FastAPI Server for Semantic Pattern Query App

REST API for querying the pattern library using the 7-layer RAG architecture.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from src.document_store.orchestrator import SemanticPatternOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Semantic Pattern Query API",
    description="Production RAG system for querying the pattern library",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator (lazy loading)
_orchestrator: Optional[SemanticPatternOrchestrator] = None


def get_orchestrator() -> SemanticPatternOrchestrator:
    """Get or create orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        # Read configuration from environment variables
        ollama_model = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
        ollama_generation_model = os.getenv("OLLAMA_GENERATION_MODEL", "qwen3:14b")
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        logger.info(f"Creating orchestrator with ollama_model={ollama_model}, generation_model={ollama_generation_model}")

        _orchestrator = SemanticPatternOrchestrator(
            ollama_model=ollama_model,
            ollama_generation_model=ollama_generation_model,
            ollama_base_url=ollama_base_url
        )
    return _orchestrator


# Request/Response models
class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    top_k: int = 10
    use_cache: bool = True
    user_context: Optional[Dict[str, Any]] = None
    query_embedder_type: Optional[str] = None  # "ollama" or "gemini"


class QueryResponse(BaseModel):
    """Query response model."""
    answer: str
    sources: List[Dict[str, Any]]
    cache_hit: bool
    retrieved_docs: int
    context_docs_used: Optional[int] = None


class StatsResponse(BaseModel):
    """Stats response model."""
    qdrant: Dict[str, Any]
    embedding_models: Dict[str, str]
    vector_dimension: int


class IngestRequest(BaseModel):
    """Ingest request model."""
    directory_path: Optional[str] = None
    pattern: str = "**/*.md"
    force_reingest: bool = False


class IngestResponse(BaseModel):
    """Ingest response model."""
    status: str
    files_processed: int
    total_chunks: int
    message: str
    stats: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Semantic Pattern Query API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        orchestrator = get_orchestrator()
        stats = orchestrator.get_stats()
        return {
            "status": "healthy",
            "services": {
                "qdrant": "connected",
                "elasticsearch": "connected",
                "redis": "connected",
                "ollama": "connected"
            },
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the pattern library.
    
    Args:
        request: Query request with query text and options
            - query_embedder_type: "ollama" (default) or "gemini" for query space embeddings
        
    Returns:
        Query response with answer, sources, and metadata
    """
    try:
        # Validate query_embedder_type
        if request.query_embedder_type and request.query_embedder_type not in ["ollama", "gemini"]:
            raise HTTPException(
                status_code=400,
                detail=f"query_embedder_type must be 'ollama' or 'gemini', got: {request.query_embedder_type}"
            )
        
        orchestrator = get_orchestrator()
        result = orchestrator.query(
            query=request.query,
            top_k=request.top_k,
            use_cache=request.use_cache,
            user_context=request.user_context,
            query_embedder_type=request.query_embedder_type
        )
        
        return QueryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def stats():
    """
    Get system statistics.
    
    Returns:
        System statistics
    """
    try:
        orchestrator = get_orchestrator()
        stats_data = orchestrator.get_stats()
        return StatsResponse(**stats_data)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Trigger ingestion of pattern library.
    
    This endpoint processes all markdown files from the specified directory
    and ingests them into Qdrant and Elasticsearch.
    
    Args:
        request: Ingest request with directory path and options
        background_tasks: FastAPI background tasks (for future async processing)
        
    Returns:
        Ingest response with status and statistics
    """
    import os
    from pathlib import Path
    
    try:
        orchestrator = get_orchestrator()
        
        # Determine directory path
        if request.directory_path:
            directory_path = request.directory_path
        else:
            # Use default pattern library path
            directory_path = os.getenv(
                "PATTERN_LIBRARY_PATH",
                "../pattern-library"
            )
        
        directory = Path(directory_path)
        if not directory.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Directory not found: {directory_path}"
            )
        
        logger.info(f"Starting ingestion from: {directory_path}")
        logger.info(f"Pattern: {request.pattern}, Force reingest: {request.force_reingest}")
        
        # Count files before ingestion
        files_before = list(directory.glob(request.pattern))
        files_count = len(files_before)
        
        if files_count == 0:
            return IngestResponse(
                status="error",
                files_processed=0,
                total_chunks=0,
                message=f"No files found matching pattern '{request.pattern}' in {directory_path}",
                stats=None
            )
        
        # Perform ingestion
        # Note: This is a blocking operation - for large datasets, consider
        # using background tasks or a job queue
        total_chunks = 0
        files_processed = 0
        errors = []
        
        for file_path in files_before:
            try:
                chunks = orchestrator.ingest_document(
                    str(file_path),
                    force_reingest=request.force_reingest
                )
                total_chunks += chunks
                files_processed += 1
                if files_processed % 10 == 0:
                    logger.info(f"Processed {files_processed}/{files_count} files...")
            except Exception as e:
                error_msg = f"Error ingesting {file_path.name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue
        
        # Get updated stats
        stats_data = orchestrator.get_stats()
        
        message = f"Successfully ingested {files_processed}/{files_count} files, {total_chunks} total chunks"
        if errors:
            message += f" ({len(errors)} errors)"
        
        return IngestResponse(
            status="success" if files_processed > 0 else "error",
            files_processed=files_processed,
            total_chunks=total_chunks,
            message=message,
            stats=stats_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

