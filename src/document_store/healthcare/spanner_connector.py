"""
Cloud Spanner connector for healthcare analytical data access.

Provides access to Spanner for analytical and reporting queries
used in healthcare summarization.
"""

from typing import Dict, Any, Optional, List
import logging

try:
    from google.cloud import spanner
    SPANNER_AVAILABLE = True
except ImportError:
    SPANNER_AVAILABLE = False
    spanner = None

logger = logging.getLogger(__name__)


class SpannerConnector:
    """
    Connector for accessing healthcare analytical data from Cloud Spanner.
    
    Supports analytical queries and reporting data access.
    """

    def __init__(
        self,
        project_id: str,
        instance_id: str,
        database_id: str,
    ):
        """
        Initialize Spanner connector.
        
        Args:
            project_id: Google Cloud project ID
            instance_id: Spanner instance ID
            database_id: Spanner database ID
        """
        if not SPANNER_AVAILABLE:
            raise ImportError(
                "google-cloud-spanner is not installed. "
                "Install it with: pip install google-cloud-spanner"
            )
        
        self.project_id = project_id
        self.instance_id = instance_id
        self.database_id = database_id
        
        self.client = spanner.Client(project=project_id)
        self.instance = self.client.instance(instance_id)
        self.database = self.instance.database(database_id)
        
        logger.info(
            f"SpannerConnector initialized: "
            f"project={project_id}, instance={instance_id}, database={database_id}"
        )

    def query_patients(
        self,
        patient_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query patient data from Spanner.
        
        Args:
            patient_id: Optional specific patient ID
            
        Returns:
            List of patient records
        """
        if patient_id:
            query = "SELECT * FROM patients WHERE patient_id = @patient_id"
            params = {"patient_id": patient_id}
        else:
            query = "SELECT * FROM patients LIMIT 100"
            params = {}
        
        try:
            with self.database.snapshot() as snapshot:
                results = snapshot.execute_sql(query, params=params)
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error querying patients: {e}")
            raise

    def query_analytical_data(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute analytical query on Spanner.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Query results as list of dictionaries
        """
        try:
            with self.database.snapshot() as snapshot:
                results = snapshot.execute_sql(query, params=params or {})
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error executing analytical query: {e}")
            raise

