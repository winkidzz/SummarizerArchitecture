"""
Example: Healthcare data integration with RAG patterns.

Demonstrates integration with FHIR APIs, BigQuery, Spanner,
and real-time Pub/Sub events for healthcare summarization.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.orchestrator import DocumentStoreOrchestrator
import logging

# Try to import healthcare connectors
try:
    from document_store.healthcare.fhir_client import FHIRClient
    from document_store.healthcare.bigquery_connector import BigQueryConnector
    from document_store.healthcare.spanner_connector import SpannerConnector
    from document_store.healthcare.pubsub_events import PubSubEventHandler
    HEALTHCARE_AVAILABLE = True
except ImportError:
    HEALTHCARE_AVAILABLE = False
    logging.warning("Healthcare connectors not available. Install: pip install google-cloud-bigquery google-cloud-spanner google-cloud-pubsub fhir.resources")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_fhir_rag():
    """Example: RAG summarization using FHIR API data."""
    if not HEALTHCARE_AVAILABLE:
        logger.warning("Healthcare connectors not available")
        return
    
    # Initialize FHIR client
    fhir_client = FHIRClient(
        base_url="https://fhir.example.com/fhir",
        auth_token="your_token_here",
    )
    
    # Get patient data via FHIR
    patient_id = "12345"
    patient_data = fhir_client.get_patient_summary_data(patient_id)
    
    # Initialize RAG orchestrator
    orchestrator = DocumentStoreOrchestrator()
    
    # Ingest patient data
    # Convert FHIR data to document format
    patient_doc = {
        "content": str(patient_data),
        "metadata": {
            "patient_id": patient_id,
            "source": "fhir",
            "pattern_type": "healthcare-summarization",
        }
    }
    orchestrator.vector_store.add_documents([patient_doc])
    
    # Query with RAG
    summary = orchestrator.query_patterns(
        query=f"Summarize patient {patient_id} medical history",
        use_agent=True,  # Use Google ADK agent
    )
    
    logger.info(f"FHIR RAG Summary: {summary}")


def example_bigquery_rag():
    """Example: RAG summarization using BigQuery data."""
    if not HEALTHCARE_AVAILABLE:
        logger.warning("Healthcare connectors not available")
        return
    
    # Initialize BigQuery connector
    bq_connector = BigQueryConnector(
        project_id="healthcare-project",
        dataset_id="healthcare_data",
    )
    
    # Query patient data
    patient_id = "12345"
    patient_data = bq_connector.get_patient_summary_data(patient_id)
    
    # Initialize RAG orchestrator
    orchestrator = DocumentStoreOrchestrator()
    
    # Ingest and summarize
    patient_doc = {
        "content": str(patient_data),
        "metadata": {
            "patient_id": patient_id,
            "source": "bigquery",
            "pattern_type": "healthcare-summarization",
        }
    }
    orchestrator.vector_store.add_documents([patient_doc])
    
    # Query with RAG
    summary = orchestrator.query_patterns(
        query="Summarize patient encounters and treatment history",
        use_agent=True,
    )
    
    logger.info(f"BigQuery RAG Summary: {summary}")


def example_realtime_pubsub():
    """Example: Real-time RAG with Pub/Sub events."""
    if not HEALTHCARE_AVAILABLE:
        logger.warning("Healthcare connectors not available")
        return
    
    orchestrator = DocumentStoreOrchestrator()
    
    # Initialize Pub/Sub handler
    pubsub_handler = PubSubEventHandler(
        project_id="healthcare-project",
        subscription_id="adt-events-sub",
    )
    
    def process_adt_event(event_data):
        """Process ADT (Admission, Discharge, Transfer) event."""
        logger.info(f"Processing ADT event: {event_data}")
        
        # Real-time summarization
        if event_data.get('event_type') == 'ADMISSION':
            summary = orchestrator.query_patterns(
                query=f"Generate admission summary: {event_data}",
                use_ollama_rag=True,  # Real-time processing
            )
            logger.info(f"Admission summary: {summary}")
        
        return summary
    
    # Subscribe to real-time events
    logger.info("Subscribing to Pub/Sub events...")
    pubsub_handler.subscribe(callback=process_adt_event)


def example_multi_source_rag():
    """Example: RAG with multiple healthcare data sources."""
    if not HEALTHCARE_AVAILABLE:
        logger.warning("Healthcare connectors not available")
        return
    
    patient_id = "12345"
    orchestrator = DocumentStoreOrchestrator()
    
    # Get data from multiple sources
    sources = []
    
    # FHIR data
    try:
        fhir_client = FHIRClient(base_url="https://fhir.example.com/fhir")
        fhir_data = fhir_client.get_patient_summary_data(patient_id)
        sources.append({
            "content": str(fhir_data),
            "metadata": {"source": "fhir", "patient_id": patient_id}
        })
    except Exception as e:
        logger.warning(f"FHIR access failed: {e}")
    
    # BigQuery data
    try:
        bq_connector = BigQueryConnector(
            project_id="healthcare-project",
            dataset_id="healthcare_data",
        )
        bq_data = bq_connector.get_patient_summary_data(patient_id)
        sources.append({
            "content": str(bq_data),
            "metadata": {"source": "bigquery", "patient_id": patient_id}
        })
    except Exception as e:
        logger.warning(f"BigQuery access failed: {e}")
    
    # Ingest all sources
    if sources:
        orchestrator.vector_store.add_documents(sources)
        
        # Multi-source RAG query
        summary = orchestrator.query_patterns(
            query=f"Summarize patient {patient_id} from all available sources",
            use_agent=True,  # ADK agent handles multi-source
        )
        
        logger.info(f"Multi-source RAG Summary: {summary}")


def main():
    """Run healthcare data integration examples."""
    logger.info("Healthcare Data Integration Examples")
    logger.info("=" * 60)
    
    # Example 1: FHIR RAG
    logger.info("\nExample 1: FHIR API RAG")
    try:
        example_fhir_rag()
    except Exception as e:
        logger.error(f"FHIR example failed: {e}")
    
    # Example 2: BigQuery RAG
    logger.info("\nExample 2: BigQuery RAG")
    try:
        example_bigquery_rag()
    except Exception as e:
        logger.error(f"BigQuery example failed: {e}")
    
    # Example 3: Real-time Pub/Sub
    logger.info("\nExample 3: Real-time Pub/Sub Events")
    logger.info("(This would run continuously - commented out for demo)")
    # example_realtime_pubsub()
    
    # Example 4: Multi-source RAG
    logger.info("\nExample 4: Multi-Source RAG")
    try:
        example_multi_source_rag()
    except Exception as e:
        logger.error(f"Multi-source example failed: {e}")


if __name__ == "__main__":
    main()

