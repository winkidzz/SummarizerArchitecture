"""
Example: How to integrate telemetry into your RAG pipeline

This file shows how to add telemetry to the orchestrator and API server.
"""

from typing import Dict, Any, Optional
import time
from .telemetry import QueryTelemetry
from .metrics import MetricsCollector
from .logger import StructuredLogger

# Initialize components
metrics = MetricsCollector()
logger = StructuredLogger(__name__)


# ============================================================================
# Example 1: Instrumenting the API Server
# ============================================================================

def example_api_integration(query: str, user_context: Optional[Dict[str, Any]] = None):
    """
    Example of how to add telemetry to API endpoints.
    
    This would be integrated into api_server.py's query endpoint.
    """
    # Create telemetry tracker
    telemetry = QueryTelemetry(query=query, user_context=user_context)
    telemetry.start()
    
    try:
        # Your existing query logic here
        # For example:
        # result = orchestrator.query(...)
        
        # Record metrics at each stage
        # Example: After retrieval
        telemetry.record_retrieval(
            retriever_type="hybrid",
            stage="final",
            duration=0.5,  # Actual duration
            doc_count=5,
            avg_score=0.85
        )
        
        # Example: After generation
        telemetry.record_generation(
            model_type="qwen3:14b",
            duration=2.0,
            tokens=500
        )
        
        # Finish tracking
        telemetry_data = telemetry.finish(
            status="success",
            answer="Example answer",
            sources=[]
        )
        
        return {
            "answer": "Example answer",
            "telemetry": telemetry_data
        }
    
    except Exception as e:
        telemetry.finish(status="error")
        logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            query_id=telemetry.query_id
        )
        raise


# ============================================================================
# Example 2: Instrumenting the Orchestrator
# ============================================================================

def example_orchestrator_integration(
    query: str,
    top_k: int = 10,
    use_cache: bool = True,
    user_context: Optional[Dict[str, Any]] = None
):
    """
    Example of how to add telemetry to orchestrator.query().
    
    This shows the pattern for instrumenting the main query method.
    """
    telemetry = QueryTelemetry(query=query, user_context=user_context)
    telemetry.start()
    
    # Check cache
    if use_cache:
        cache_start = time.time()
        # ... cache check logic ...
        cache_duration = time.time() - cache_start
        telemetry.record_cache(hit=False)  # or True if cache hit
        telemetry.record_stage("cache_check", cache_duration)
    
    # Embedding
    embed_start = time.time()
    # ... embedding logic ...
    embed_duration = time.time() - embed_start
    telemetry.record_embedding(
        embedder_type="ollama",
        duration=embed_duration
    )
    
    # Retrieval
    retrieval_start = time.time()
    # ... retrieval logic ...
    retrieval_duration = time.time() - retrieval_start
    telemetry.record_retrieval(
        retriever_type="hybrid",
        stage="final",
        duration=retrieval_duration,
        doc_count=5,
        avg_score=0.85
    )
    
    # Generation
    gen_start = time.time()
    # ... generation logic ...
    gen_duration = time.time() - gen_start
    telemetry.record_generation(
        model_type="qwen3:14b",
        duration=gen_duration,
        tokens=500
    )
    
    # Finish
    return telemetry.finish(status="success")


# ============================================================================
# Example 3: Using Context Managers
# ============================================================================

from .telemetry import TelemetryContext

def example_context_manager():
    """Example using TelemetryContext for automatic timing."""
    
    with TelemetryContext("retrieval", operation_type="retrieval", query_id="123"):
        # Your retrieval code here
        time.sleep(0.1)  # Simulated work
        # Context manager automatically logs start/end and handles errors


# ============================================================================
# Example 4: Adding Prometheus Metrics Endpoint
# ============================================================================

"""
In api_server.py, add:

from prometheus_client import make_asgi_app
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Create metrics app
metrics_app = make_asgi_app()

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
"""


# ============================================================================
# Example 5: Custom Metrics
# ============================================================================

def example_custom_metrics():
    """Example of recording custom business metrics."""
    
    # Record user feedback
    metrics.user_feedback.labels(rating="positive").inc()
    
    # Record query complexity
    metrics.query_complexity.observe(0.75)
    
    # Update cache size
    metrics.update_cache_size("semantic", 1000)
    
    # Update vector store size
    metrics.update_vector_store_size(5000)

