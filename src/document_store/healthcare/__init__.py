"""
Healthcare data integration modules for RAG patterns.

Provides integration with FHIR APIs, proprietary EHR APIs,
BigQuery, Spanner, and real-time streaming data sources.
"""

from .fhir_client import FHIRClient
from .ehr_client import EHRClient
from .bigquery_connector import BigQueryConnector
from .spanner_connector import SpannerConnector
from .pubsub_events import PubSubEventHandler

__all__ = [
    "FHIRClient",
    "EHRClient",
    "BigQueryConnector",
    "SpannerConnector",
    "PubSubEventHandler",
]

__version__ = "0.1.0"

