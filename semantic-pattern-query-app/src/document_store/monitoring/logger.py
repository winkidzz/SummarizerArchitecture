"""
Structured JSON Logging for RAG System

Provides HIPAA-compliant structured logging with PHI redaction.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import traceback


class StructuredLogger:
    """Structured JSON logger for telemetry and audit logging."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        # Use JSON formatter
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(level)
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from context (HIPAA compliance)."""
        sanitized = context.copy()
        
        # PHI fields to redact
        phi_fields = [
            'patient_id', 'patient_name', 'ssn', 'date_of_birth',
            'medical_record_number', 'api_key', 'password', 'token'
        ]
        
        for key in phi_fields:
            if key in sanitized:
                sanitized[key] = "[REDACTED]"
        
        # Recursively sanitize nested dictionaries
        for key, value in sanitized.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_context(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_context(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return sanitized
    
    def log_query_start(
        self,
        query: str,
        query_id: str,
        user_context: Dict[str, Any],
        **kwargs
    ):
        """Log query start event."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "query_start",
            "query_id": query_id,
            "query_length": len(query),
            "query_preview": query[:100] + "..." if len(query) > 100 else query,
            "user_context": self._sanitize_context(user_context),
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_query_end(
        self,
        query_id: str,
        duration_ms: float,
        cache_hit: bool,
        retrieved_docs: int,
        embedder_type: str,
        answer_length: int,
        citation_count: int,
        status: str = "success",
        stage_timings: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """Log query completion event."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "query_end",
            "query_id": query_id,
            "duration_ms": duration_ms,
            "cache_hit": cache_hit,
            "retrieved_docs": retrieved_docs,
            "embedder_type": embedder_type,
            "answer_length": answer_length,
            "citation_count": citation_count,
            "status": status,
            "stage_timings": stage_timings or {},
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_stage(
        self,
        query_id: str,
        stage: str,
        duration_ms: float,
        **metadata
    ):
        """Log pipeline stage execution."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "stage",
            "query_id": query_id,
            "stage": stage,
            "duration_ms": duration_ms,
            **metadata
        }
        self.logger.debug(json.dumps(log_entry))
    
    def log_operation_start(
        self,
        operation: str,
        operation_type: str,
        query_id: str,
        span_id: str,
        **context
    ):
        """Log operation start (for tracing)."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "operation_start",
            "operation": operation,
            "operation_type": operation_type,
            "query_id": query_id,
            "span_id": span_id,
            **self._sanitize_context(context)
        }
        self.logger.debug(json.dumps(log_entry))
    
    def log_operation_end(
        self,
        operation: str,
        query_id: str,
        span_id: str,
        duration_ms: float,
        **context
    ):
        """Log operation end (for tracing)."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "operation_end",
            "operation": operation,
            "query_id": query_id,
            "span_id": span_id,
            "duration_ms": duration_ms,
            **self._sanitize_context(context)
        }
        self.logger.debug(json.dumps(log_entry))
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        query_id: Optional[str] = None,
        span_id: Optional[str] = None,
        operation: Optional[str] = None,
        stack_trace: Optional[str] = None,
        **kwargs
    ):
        """Log error with full context."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "query_id": query_id,
            "span_id": span_id,
            "operation": operation,
            "stack_trace": stack_trace,
            **self._sanitize_context(kwargs)
        }
        self.logger.error(json.dumps(log_entry))
    
    def log_audit(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: str,
        **metadata
    ):
        """Log HIPAA-compliant audit event."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "audit",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result,
            **self._sanitize_context(metadata)
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_type: str = "gauge",
        **labels
    ):
        """Log custom metric."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "metric",
            "metric_name": metric_name,
            "metric_value": metric_value,
            "metric_type": metric_type,
            **labels
        }
        self.logger.info(json.dumps(log_entry))


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Extract message (should already be JSON)
        if isinstance(record.msg, str):
            try:
                # If it's already JSON, return as-is
                json.loads(record.msg)
                return record.msg
            except json.JSONDecodeError:
                # If not JSON, wrap it
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.msg,
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)
        else:
            # Non-string message
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": str(record.msg),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_data)

