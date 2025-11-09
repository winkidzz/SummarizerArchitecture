"""
Document Store for AI Summarization Reference Architecture

This package provides document processing, storage, and retrieval capabilities
for the architecture pattern knowledge base.
"""

from .processors.docling_processor import DoclingProcessor
from .storage.vector_store import VectorStore
from .search.rag_query import RAGQueryInterface
from .search.web_search import WebSearchTool
from .agents.adk_agent import ADKAgentQuery
from .agents.ollama_agent import OllamaAgent

# Healthcare data integration (optional)
try:
    from .healthcare.fhir_client import FHIRClient
    from .healthcare.ehr_client import EHRClient
    from .healthcare.bigquery_connector import BigQueryConnector
    from .healthcare.spanner_connector import SpannerConnector
    from .healthcare.pubsub_events import PubSubEventHandler
    HEALTHCARE_AVAILABLE = True
except ImportError:
    HEALTHCARE_AVAILABLE = False
    FHIRClient = None
    EHRClient = None
    BigQueryConnector = None
    SpannerConnector = None
    PubSubEventHandler = None

__all__ = [
    "DoclingProcessor",
    "VectorStore",
    "RAGQueryInterface",
    "WebSearchTool",
    "ADKAgentQuery",
    "OllamaAgent",
]

if HEALTHCARE_AVAILABLE:
    __all__.extend([
        "FHIRClient",
        "EHRClient",
        "BigQueryConnector",
        "SpannerConnector",
        "PubSubEventHandler",
    ])

__version__ = "0.1.0"

