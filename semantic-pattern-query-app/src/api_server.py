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
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import time

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.document_store.orchestrator import SemanticPatternOrchestrator
from src.document_store.monitoring import QueryTelemetry, StructuredLogger, MetricsCollector
from src.document_store.evaluation import evaluate_answer_quality, evaluate_context_quality

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
telemetry_logger = StructuredLogger(__name__)

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

        # Read Elasticsearch URL from environment
        # Default to local Elasticsearch instance
        elasticsearch_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

        # Read web search configuration
        enable_web_search = os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true"
        web_search_provider = os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo")

        logger.info(f"Creating orchestrator with ollama_model={ollama_model}, generation_model={ollama_generation_model}, elasticsearch_url={elasticsearch_url}, enable_web_search={enable_web_search}")

        _orchestrator = SemanticPatternOrchestrator(
            ollama_model=ollama_model,
            ollama_generation_model=ollama_generation_model,
            ollama_base_url=ollama_base_url,
            elasticsearch_url=elasticsearch_url,
            enable_web_search=enable_web_search,
            web_search_provider_type=web_search_provider
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
    enable_web_search: bool = False  # Enable web search augmentation
    web_mode: str = "on_low_confidence"  # "parallel" or "on_low_confidence"


class QueryResponse(BaseModel):
    """Query response model."""
    answer: str
    sources: List[Dict[str, Any]]
    cache_hit: bool
    retrieved_docs: Optional[int] = None
    context_docs_used: Optional[int] = None
    quality_metrics: Optional[Dict[str, Any]] = None  # Real-time quality metrics
    citations: Optional[List[Dict[str, Any]]] = None  # Phase 2: Citations for audit/compliance
    retrieval_stats: Optional[Dict[str, Any]] = None  # Phase 2: Tier breakdown


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
    Query the pattern library with telemetry tracking.

    Args:
        request: Query request with query text and options
            - query_embedder_type: "ollama" (default) or "gemini" for query space embeddings
            - enable_web_search: Enable web search augmentation (default: False)
            - web_mode: "parallel" (always search web) or "on_low_confidence" (conditional)

    Returns:
        Query response with answer, sources, and metadata
    """
    # Initialize telemetry tracking
    telemetry = QueryTelemetry(
        query=request.query,
        user_context=request.user_context or {}
    )
    telemetry.start()

    # Log incoming request parameters for debugging
    logger.info(
        f"Query request received: enable_web_search={request.enable_web_search}, "
        f"web_mode={request.web_mode}, top_k={request.top_k}, "
        f"query_embedder_type={request.query_embedder_type}, use_cache={request.use_cache}"
    )

    try:
        # Validate query_embedder_type
        if request.query_embedder_type and request.query_embedder_type not in ["ollama", "gemini"]:
            raise HTTPException(
                status_code=400,
                detail=f"query_embedder_type must be 'ollama' or 'gemini', got: {request.query_embedder_type}"
            )

        # Validate web_mode
        if request.web_mode not in ["parallel", "on_low_confidence"]:
            raise HTTPException(
                status_code=400,
                detail=f"web_mode must be 'parallel' or 'on_low_confidence', got: {request.web_mode}"
            )
        
        # Pass telemetry to orchestrator
        orchestrator = get_orchestrator()
        result = orchestrator.query(
            query=request.query,
            top_k=request.top_k,
            use_cache=request.use_cache,
            user_context=request.user_context,
            query_embedder_type=request.query_embedder_type,
            telemetry=telemetry,  # Pass telemetry context
            enable_web_search=request.enable_web_search,  # NEW: Pass web search flag
            web_mode=request.web_mode  # NEW: Pass web search mode
        )

        # Evaluate quality metrics in real-time (runs on every query)
        quality_metrics = {}
        try:
            answer = result.get("answer", "")
            sources = result.get("sources", [])

            # Get raw retrieved documents for quality evaluation
            # We need to retrieve again to get the actual text chunks
            # (the generator compactifies them into citations)
            retrieved_docs = orchestrator.hybrid_retriever.retrieve(
                request.query,
                top_k=request.top_k,
                embedder_type=request.query_embedder_type,
                enable_web_search=request.enable_web_search,
                web_mode=request.web_mode
            )

            # Extract context chunks from retrieved docs
            context_chunks = []
            chunk_relevance_scores = []
            for doc in retrieved_docs:
                if "text" in doc:
                    context_chunks.append(doc["text"])
                    # Get score from any available field
                    score = doc.get("score") or doc.get("similarity_score") or doc.get("rrf_score", 0.5)
                    chunk_relevance_scores.append(score)

            # Evaluate answer quality (no ground truth needed)
            if answer and context_chunks:
                answer_metrics = evaluate_answer_quality(
                    query=request.query,
                    answer=answer,
                    context_chunks=context_chunks
                )

                # Record to Prometheus (automatic monitoring)
                MetricsCollector.record_answer_quality(
                    faithfulness=answer_metrics['faithfulness'],
                    relevancy=answer_metrics['relevancy'],
                    completeness=answer_metrics['completeness'],
                    citation_grounding=answer_metrics['citation_grounding'],
                    has_hallucination=answer_metrics['has_hallucination'],
                    hallucination_severity=answer_metrics['hallucination_severity']
                )

                # Evaluate context quality (no ground truth needed for relevancy & utilization)
                context_metrics = evaluate_context_quality(
                    query=request.query,
                    retrieved_chunks=context_chunks,
                    generated_answer=answer,
                    chunk_relevance_scores=chunk_relevance_scores
                )

                # Record to Prometheus
                MetricsCollector.record_context_quality(
                    precision=context_metrics['context_precision'],
                    recall=context_metrics['context_recall'],
                    relevancy=context_metrics['context_relevancy'],
                    utilization=context_metrics['context_utilization']
                )

                # Add to response (optional - can be disabled for production)
                quality_metrics = {
                    "answer": {
                        "faithfulness": answer_metrics['faithfulness'],
                        "relevancy": answer_metrics['relevancy'],
                        "completeness": answer_metrics['completeness'],
                        "has_hallucination": answer_metrics['has_hallucination'],
                        "hallucination_severity": answer_metrics['hallucination_severity']
                    },
                    "context": {
                        "relevancy": context_metrics['context_relevancy'],
                        "utilization": context_metrics['context_utilization']
                    }
                }

                # Log hallucinations (important for healthcare)
                if answer_metrics['has_hallucination']:
                    logger.warning(
                        f"Hallucination detected - Query: {request.query[:100]}, "
                        f"Severity: {answer_metrics['hallucination_severity']}, "
                        f"Unsupported claims: {answer_metrics['unsupported_claims']}"
                    )

        except Exception as e:
            # Don't fail the query if quality evaluation fails
            logger.error(f"Quality metrics evaluation failed: {e}", exc_info=True)
            quality_metrics = {"error": str(e)}

        # Add quality metrics to result
        result["quality_metrics"] = quality_metrics

        # Record final metrics
        telemetry.finish(
            status="success",
            answer=result.get("answer"),
            sources=result.get("sources", [])
        )

        return QueryResponse(**result)
    
    except HTTPException:
        telemetry.finish(status="error")
        raise
    except Exception as e:
        telemetry.finish(status="error")
        logger.error(f"Query error: {e}")
        telemetry_logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            query_id=telemetry.query_id
        )
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns:
        Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


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
    import os
    # Get port from environment or default to 8000
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

