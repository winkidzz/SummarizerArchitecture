"""
Main Telemetry Coordinator

Coordinates metrics collection, tracing, and logging across the RAG pipeline.
"""

import time
import uuid
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime

from .metrics import MetricsCollector
from .logger import StructuredLogger

# Initialize components
metrics = MetricsCollector()
logger = StructuredLogger(__name__)


class TelemetryContext:
    """Context manager for tracking operations with telemetry."""
    
    def __init__(
        self,
        operation_name: str,
        operation_type: str = "query",
        **context
    ):
        self.operation_name = operation_name
        self.operation_type = operation_type
        self.context = context
        self.start_time = None
        self.query_id = context.get("query_id", str(uuid.uuid4()))
        self.span_id = str(uuid.uuid4())
    
    def __enter__(self):
        self.start_time = time.time()
        logger.log_operation_start(
            operation=self.operation_name,
            operation_type=self.operation_type,
            query_id=self.query_id,
            span_id=self.span_id,
            **self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            logger.log_error(
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                query_id=self.query_id,
                span_id=self.span_id,
                operation=self.operation_name
            )
            metrics.record_error(exc_type.__name__)
        else:
            logger.log_operation_end(
                operation=self.operation_name,
                query_id=self.query_id,
                span_id=self.span_id,
                duration_ms=duration * 1000,
                **self.context
            )
        
        return False  # Don't suppress exceptions


class QueryTelemetry:
    """Telemetry tracking for RAG queries."""
    
    def __init__(self, query: str, user_context: Optional[Dict[str, Any]] = None):
        self.query = query
        self.user_context = user_context or {}
        self.query_id = str(uuid.uuid4())
        self.start_time = None
        self.stage_timings = {}
        self.embedder_type = None
        self.cache_hit = False
        self.retrieved_docs = 0
        self.answer_length = 0
        self.citation_count = 0
    
    def start(self):
        """Start query tracking."""
        self.start_time = time.time()
        logger.log_query_start(
            query=self.query,
            query_id=self.query_id,
            user_context=self.user_context
        )
    
    def record_stage(self, stage: str, duration: float, **metadata):
        """Record timing for a pipeline stage."""
        self.stage_timings[stage] = duration
        logger.log_stage(
            query_id=self.query_id,
            stage=stage,
            duration_ms=duration * 1000,
            **metadata
        )
    
    def record_retrieval(
        self,
        retriever_type: str,
        stage: str,
        duration: float,
        doc_count: int,
        avg_score: Optional[float] = None
    ):
        """Record retrieval metrics."""
        self.retrieved_docs = doc_count
        metrics.record_retrieval(
            retriever_type=retriever_type,
            stage=stage,
            duration=duration,
            doc_count=doc_count,
            avg_score=avg_score
        )
        self.record_stage(
            f"retrieval_{retriever_type}_{stage}",
            duration,
            doc_count=doc_count,
            avg_score=avg_score
        )
    
    def record_generation(
        self,
        model_type: str,
        duration: float,
        tokens: int
    ):
        """Record generation metrics."""
        metrics.record_generation(
            model_type=model_type,
            duration=duration,
            tokens=tokens
        )
        self.record_stage(
            "generation",
            duration,
            model_type=model_type,
            tokens=tokens
        )
    
    def record_embedding(
        self,
        embedder_type: str,
        duration: float,
        status: str = "success"
    ):
        """Record embedding metrics."""
        self.embedder_type = embedder_type
        metrics.record_embedding(
            embedder_type=embedder_type,
            duration=duration,
            status=status
        )
        self.record_stage(
            "embedding",
            duration,
            embedder_type=embedder_type
        )
    
    def record_cache(self, hit: bool, cache_type: str = "semantic"):
        """Record cache operation."""
        self.cache_hit = hit
        metrics.record_cache(
            cache_type=cache_type,
            operation="get",
            hit=hit
        )
        self.record_stage(
            "cache_check",
            0.0,  # Cache check is typically very fast
            cache_hit=hit
        )
    
    def finish(
        self,
        status: str = "success",
        answer: Optional[str] = None,
        sources: Optional[list] = None
    ):
        """Finish query tracking and record final metrics."""
        total_duration = time.time() - self.start_time
        
        if answer:
            self.answer_length = len(answer)
        if sources:
            self.citation_count = len(sources)
        
        # Record final metrics
        metrics.record_query(
            embedder_type=self.embedder_type or "unknown",
            status=status,
            cache_hit=self.cache_hit,
            duration=total_duration,
            retrieved_docs=self.retrieved_docs,
            answer_length=self.answer_length,
            citation_count=self.citation_count
        )
        
        # Log final query event
        logger.log_query_end(
            query_id=self.query_id,
            duration_ms=total_duration * 1000,
            cache_hit=self.cache_hit,
            retrieved_docs=self.retrieved_docs,
            embedder_type=self.embedder_type,
            answer_length=self.answer_length,
            citation_count=self.citation_count,
            status=status,
            stage_timings=self.stage_timings
        )
        
        return {
            "query_id": self.query_id,
            "duration_ms": total_duration * 1000,
            "cache_hit": self.cache_hit,
            "retrieved_docs": self.retrieved_docs,
            "embedder_type": self.embedder_type,
            "stage_timings": self.stage_timings
        }


def get_telemetry() -> QueryTelemetry:
    """Get current telemetry context (thread-local)."""
    # In a real implementation, this would use thread-local storage
    # For now, return a simple instance
    pass

